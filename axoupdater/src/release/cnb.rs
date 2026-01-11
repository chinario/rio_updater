use crate::Asset;
use crate::Release;
use crate::Version;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use url::Url;

/// CNB.cool API client for fetching releases
#[derive(Debug, Clone)]
pub struct CnbClient {
    /// Base URL for CNB API
    base_url: String,
    /// Bearer token for authentication
    token: Option<String>,
    /// HTTP client with timeout configuration
    client: reqwest::Client,
}

/// CNB Release response structure from API
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CnbRelease {
    /// Unique identifier for the release
    pub id: String,
    /// Release tag name
    pub tag_name: Option<String>,
    /// Release name
    pub name: String,
    /// Release description
    pub body: Option<String>,
    /// Whether this is a draft release
    pub draft: bool,
    /// Whether this is marked as latest
    pub is_latest: bool,
    /// Whether this is a pre-release
    pub prerelease: Option<bool>,
    /// Author information
    pub author: Option<CnbAuthor>,
    /// List of assets in this release
    pub assets: Vec<CnbAsset>,
    /// Creation timestamp
    pub created_at: String,
    /// Last update timestamp
    pub updated_at: Option<String>,
    /// Published timestamp
    pub published_at: Option<String>,
}

/// Asset in a CNB release
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CnbAsset {
    /// Unique identifier for the asset
    pub id: String,
    /// Asset file name
    pub name: String,
    /// Asset file size in bytes
    pub size: Option<i64>,
    /// Download URL for the asset
    pub download_url: Option<String>,
    /// Browser download URL
    pub browser_download_url: Option<String>,
    /// Content type of the asset
    pub content_type: Option<String>,
    /// Creation timestamp
    pub created_at: Option<String>,
}

/// Author information in a CNB release
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CnbAuthor {
    /// Author's username
    pub username: Option<String>,
    /// Author's display name
    pub name: Option<String>,
    /// Author's avatar URL
    pub avatar_url: Option<String>,
}

/// Repository information on CNB
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CnbRepository {
    /// Repository path (e.g., "astral-sh/uv")
    pub path: String,
    /// Repository name
    pub name: String,
    /// Repository description
    pub description: Option<String>,
}

/// Error types specific to CNB operations
#[derive(Debug, Clone, thiserror::Error)]
pub enum CnbError {
    #[error("HTTP request failed: {0}")]
    HttpError(String),

    #[error("Invalid response format: {0}")]
    InvalidResponse(String),

    #[error("API error {code}: {message}")]
    ApiError { code: i32, message: String },

    #[error("Authentication failed: {0}")]
    AuthError(String),

    #[error("Release not found: {0}")]
    NotFound(String),

    #[error("Rate limit exceeded")]
    RateLimited,

    #[error("Request timeout")]
    Timeout,

    #[error("Serialization error: {0}")]
    #[allow(dead_code)]
    SerializationError(String),
}

/// Response wrapper for API errors
#[derive(Debug, Deserialize)]
pub struct CnbErrorResponse {
    /// Error code
    #[allow(dead_code)]
    pub errcode: i32,
    /// Error message
    pub errmsg: String,
    /// Error parameters
    #[allow(dead_code)]
    pub errparam: Option<serde_json::Value>,
}

/// Pagination metadata in responses
#[derive(Debug, Deserialize)]
pub struct CnbPaginationMeta {
    /// Current page number
    #[allow(dead_code)]
    pub page: u32,
    /// Page size
    #[allow(dead_code)]
    pub page_size: u32,
    /// Total count of items
    #[allow(dead_code)]
    pub total: u32,
}

impl CnbClient {
    /// Creates a new CNB client with optional authentication token
    pub fn new(token: Option<String>) -> Self {
        Self::with_url("https://api.cnb.cool".to_string(), token)
    }

    /// Creates a new CNB client with custom base URL
    pub fn with_url(base_url: String, token: Option<String>) -> Self {
        // Build headers with required CNB API Content-Type
        let mut headers = reqwest::header::HeaderMap::new();
        headers.insert(
            reqwest::header::ACCEPT,
            "application/vnd.cnb.api+json"
                .parse()
                .unwrap_or_else(|_| reqwest::header::HeaderValue::from_static("application/json")),
        );

        let client = match reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .default_headers(headers)
            .build()
        {
            Ok(c) => c,
            Err(_) => reqwest::Client::new(),
        };

        Self {
            base_url,
            token,
            client,
        }
    }

    /// Sets the authentication token
    #[allow(dead_code)]
    pub fn set_token(&mut self, token: String) {
        self.token = Some(token);
    }

    /// Builds the authorization header value
    fn auth_header(&self) -> Option<String> {
        self.token.as_ref().map(|t| format!("Bearer {}", t))
    }

    /// Builds a URL for the given path
    fn build_url(&self, path: &str) -> Result<Url, CnbError> {
        Url::parse(&format!("{}{}", self.base_url, path))
            .map_err(|e| CnbError::HttpError(format!("Invalid URL: {}", e)))
    }

    /// Executes a request with retry logic
    async fn execute_with_retry<T: for<'de> Deserialize<'de>>(
        &self,
        method: &str,
        url: &str,
        max_retries: u32,
    ) -> Result<T, CnbError> {
        let mut last_error = None;

        for attempt in 0..=max_retries {
            match self.execute_request::<T>(method, url).await {
                Ok(response) => return Ok(response),
                Err(e) => {
                    last_error = Some(e.clone());

                    // Don't retry on client errors (4xx) except timeout
                    if let CnbError::Timeout = e {
                        if attempt < max_retries {
                            // Exponential backoff: 1s, 2s, 4s
                            let delay_secs = 1u64 << attempt;
                            // Use standard library sleep since tokio may not be available
                            std::thread::sleep(Duration::from_secs(delay_secs));
                            continue;
                        }
                    } else if let CnbError::HttpError(msg) = &e {
                        if msg.contains("timeout") && attempt < max_retries {
                            let delay_secs = 1u64 << attempt;
                            std::thread::sleep(Duration::from_secs(delay_secs));
                            continue;
                        }
                    }

                    return Err(e);
                }
            }
        }

        Err(last_error.unwrap_or_else(|| CnbError::HttpError("Unknown error".to_string())))
    }

    /// Executes a single HTTP request
    async fn execute_request<T: for<'de> Deserialize<'de>>(
        &self,
        method: &str,
        url: &str,
    ) -> Result<T, CnbError> {
        let parsed_url =
            Url::parse(url).map_err(|e| CnbError::HttpError(format!("Invalid URL: {}", e)))?;

        let mut request = match method {
            "GET" => self.client.get(parsed_url),
            "POST" => self.client.post(parsed_url),
            "PATCH" => self.client.patch(parsed_url),
            "DELETE" => self.client.delete(parsed_url),
            _ => {
                return Err(CnbError::HttpError(format!(
                    "Unsupported method: {}",
                    method
                )))
            }
        };

        // Add authentication header if token is present
        if let Some(auth) = self.auth_header() {
            request = request.header("Authorization", auth);
        }

        let response = request.send().await.map_err(|e| {
            if e.is_timeout() {
                CnbError::Timeout
            } else {
                CnbError::HttpError(e.to_string())
            }
        })?;

        let status = response.status();

        match status.as_u16() {
            200..=299 => response
                .json::<T>()
                .await
                .map_err(|e| CnbError::InvalidResponse(e.to_string())),
            401 | 403 => {
                let error_body: Result<CnbErrorResponse, _> = response.json().await;
                Err(CnbError::AuthError(
                    error_body
                        .map(|e| e.errmsg)
                        .unwrap_or_else(|_| "Unauthorized".to_string()),
                ))
            }
            404 => Err(CnbError::NotFound("Resource not found".to_string())),
            429 => Err(CnbError::RateLimited),
            _ => {
                let error_body: Result<CnbErrorResponse, _> = response.json().await;
                Err(CnbError::ApiError {
                    code: status.as_u16() as i32,
                    message: error_body
                        .map(|e| e.errmsg)
                        .unwrap_or_else(|_| format!("HTTP {}", status.as_u16())),
                })
            }
        }
    }

    /// Fetches the latest release for a repository
    #[allow(dead_code)]
    pub async fn fetch_latest_release(&self, repo: &str) -> Result<CnbRelease, CnbError> {
        let path = format!("/{}/-/releases/latest", repo);
        let url = self.build_url(&path)?.to_string();

        self.execute_with_retry("GET", &url, 3).await
    }

    /// Fetches a specific release by tag
    pub async fn fetch_release_by_tag(
        &self,
        repo: &str,
        tag: &str,
    ) -> Result<CnbRelease, CnbError> {
        let path = format!("/{}/-/releases/tags/{}", repo, tag);
        let url = self.build_url(&path)?.to_string();

        self.execute_with_retry("GET", &url, 3).await
    }

    /// Fetches a specific release by ID
    #[allow(dead_code)]
    pub async fn fetch_release_by_id(
        &self,
        repo: &str,
        release_id: &str,
    ) -> Result<CnbRelease, CnbError> {
        let path = format!("/{}/-/releases/{}", repo, release_id);
        let url = self.build_url(&path)?.to_string();

        self.execute_with_retry("GET", &url, 3).await
    }

    /// Lists all releases for a repository
    pub async fn list_releases(
        &self,
        repo: &str,
        page: Option<u32>,
        page_size: Option<u32>,
    ) -> Result<Vec<CnbRelease>, CnbError> {
        let mut path = format!("/{}/-/releases", repo);

        let mut query_params = Vec::new();
        if let Some(p) = page {
            query_params.push(format!("page={}", p));
        }
        if let Some(ps) = page_size {
            query_params.push(format!("page_size={}", ps));
        }

        if !query_params.is_empty() {
            path.push('?');
            path.push_str(&query_params.join("&"));
        }

        let url = self.build_url(&path)?.to_string();

        self.execute_with_retry("GET", &url, 3).await
    }

    /// Downloads an asset from a release
    #[allow(dead_code)]
    pub async fn download_asset(
        &self,
        repo: &str,
        tag: &str,
        filename: &str,
    ) -> Result<reqwest::Response, CnbError> {
        let path = format!("/{}/-/releases/download/{}/{}", repo, tag, filename);
        let url = self.build_url(&path)?;

        let mut request = self.client.get(url);

        // Add authentication header if token is present
        if let Some(auth) = self.auth_header() {
            request = request.header("Authorization", auth);
        }

        request.send().await.map_err(|e| {
            if e.is_timeout() {
                CnbError::Timeout
            } else {
                CnbError::HttpError(e.to_string())
            }
        })
    }

    /// Gets the download URL for an asset (handles 302 redirects)
    #[allow(dead_code)]
    pub async fn get_asset_download_url(
        &self,
        repo: &str,
        tag: &str,
        filename: &str,
    ) -> Result<String, CnbError> {
        let response = self.download_asset(repo, tag, filename).await?;

        // Check if we got a 302 redirect
        if response.status() == 302 {
            if let Some(location) = response.headers().get("location") {
                return location.to_str().map(String::from).map_err(|_| {
                    CnbError::InvalidResponse("Invalid redirect location".to_string())
                });
            }
        }

        Err(CnbError::InvalidResponse(
            "Expected 302 redirect".to_string(),
        ))
    }
}

/// Helper function to convert a CnbRelease to the unified Release struct
pub fn cnb_release_to_release(cnb_release: CnbRelease, repo: &str) -> Release {
    let tag_name = cnb_release
        .tag_name
        .clone()
        .unwrap_or_else(|| cnb_release.id.clone());

    let version = Version::parse(&tag_name).unwrap_or_else(|_| {
        // If parsing fails, return a minimal version
        // Try without 'v' prefix if it has one
        let tag_no_v = tag_name.trim_start_matches('v');
        Version::parse(tag_no_v).unwrap_or_else(|_| {
            // As last resort, try to parse just as "0.0.0"
            Version::parse("0.0.0").expect("Failed to parse fallback version")
        })
    });

    let assets = cnb_release
        .assets
        .iter()
        .map(|asset| Asset {
            url: asset.download_url.clone().unwrap_or_default(),
            browser_download_url: asset.browser_download_url.clone().unwrap_or_default(),
            name: asset.name.clone(),
        })
        .collect();

    let url = format!("https://cnb.cool/{}/releases", repo);

    Release {
        tag_name,
        version,
        name: cnb_release.name,
        url,
        assets,
        prerelease: cnb_release.prerelease.unwrap_or(false),
    }
}

/// Get a specific CNB release by version
pub(crate) async fn get_specific_cnb_version(
    name: &str,
    owner: &str,
    app_name: &str,
    version: &crate::Version,
    token: &Option<String>,
) -> crate::AxoupdateResult<crate::Release> {
    let client = CnbClient::new(token.clone());
    let repo = owner; // repo is in format "owner/name"

    // Find release matching this version
    let releases = client
        .list_releases(repo, None, Some(100))
        .await
        .map_err(|_e| crate::AxoupdateError::ReleaseNotFound {
            name: name.to_owned(),
            app_name: app_name.to_owned(),
        })?;

    let release = releases
        .into_iter()
        .find(|r| {
            if let Some(tag) = &r.tag_name {
                if let Ok(parsed_version) = crate::Version::parse(tag) {
                    return parsed_version == *version;
                }
            }
            false
        })
        .ok_or_else(|| crate::AxoupdateError::ReleaseNotFound {
            name: name.to_owned(),
            app_name: app_name.to_owned(),
        })?;

    Ok(cnb_release_to_release(release, repo))
}

/// Get a specific CNB release by tag
pub(crate) async fn get_specific_cnb_tag(
    name: &str,
    owner: &str,
    app_name: &str,
    tag: &str,
    token: &Option<String>,
) -> crate::AxoupdateResult<crate::Release> {
    let client = CnbClient::new(token.clone());
    let repo = owner;

    let release = client.fetch_release_by_tag(repo, tag).await.map_err(|_e| {
        crate::AxoupdateError::ReleaseNotFound {
            name: name.to_owned(),
            app_name: app_name.to_owned(),
        }
    })?;

    Ok(cnb_release_to_release(release, repo))
}

/// Get all CNB releases for a repository
pub(crate) async fn get_cnb_releases(
    name: &str,
    owner: &str,
    app_name: &str,
    token: &Option<String>,
) -> crate::AxoupdateResult<Vec<crate::Release>> {
    let client = CnbClient::new(token.clone());
    let repo = owner;

    let releases = client
        .list_releases(repo, None, Some(100))
        .await
        .map_err(|_e| crate::AxoupdateError::ReleaseNotFound {
            name: name.to_owned(),
            app_name: app_name.to_owned(),
        })?;

    let mut result: Vec<crate::Release> = releases
        .into_iter()
        .map(|r| cnb_release_to_release(r, repo))
        .collect();

    // Sort by version descending
    result.sort_by(|a, b| b.version.cmp(&a.version));

    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cnb_client_creation() {
        let client = CnbClient::new(Some("test_token".to_string()));
        assert_eq!(client.base_url, "https://api.cnb.cool");
        assert_eq!(client.token, Some("test_token".to_string()));
    }

    #[test]
    fn test_cnb_client_with_custom_url() {
        let client = CnbClient::with_url("https://custom.cnb.cool".to_string(), None);
        assert_eq!(client.base_url, "https://custom.cnb.cool");
        assert_eq!(client.token, None);
    }

    #[test]
    fn test_auth_header_with_token() {
        let client = CnbClient::new(Some("my_token".to_string()));
        assert_eq!(client.auth_header(), Some("Bearer my_token".to_string()));
    }

    #[test]
    fn test_auth_header_without_token() {
        let client = CnbClient::new(None);
        assert_eq!(client.auth_header(), None);
    }

    #[test]
    fn test_build_url() {
        let client = CnbClient::new(None);
        let url = client.build_url("/astral-sh/uv/-/releases").unwrap();
        assert_eq!(
            url.to_string(),
            "https://api.cnb.cool/astral-sh/uv/-/releases"
        );
    }

    #[test]
    fn test_cnb_release_to_release_conversion() {
        let cnb_release = CnbRelease {
            id: "release_001".to_string(),
            tag_name: Some("v0.9.18".to_string()),
            name: "Version 0.9.18".to_string(),
            body: Some("Release notes".to_string()),
            draft: false,
            is_latest: true,
            prerelease: Some(false),
            author: None,
            assets: vec![CnbAsset {
                id: "asset_001".to_string(),
                name: "app.tar.gz".to_string(),
                size: Some(1024),
                download_url: Some("https://api.cnb.cool/download".to_string()),
                browser_download_url: Some("https://cnb.cool/download".to_string()),
                content_type: Some("application/gzip".to_string()),
                created_at: None,
            }],
            created_at: "2025-01-01T00:00:00Z".to_string(),
            updated_at: None,
            published_at: None,
        };

        let release = cnb_release_to_release(cnb_release, "astral-sh/uv");

        assert_eq!(release.tag_name, "v0.9.18");
        assert_eq!(release.name, "Version 0.9.18");
        assert_eq!(release.prerelease, false);
        assert_eq!(release.assets.len(), 1);
        assert_eq!(release.assets[0].name, "app.tar.gz");
    }
}
