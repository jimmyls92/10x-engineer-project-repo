/**
 * The one place the frontend talks HTTP: base URL, fetch wrapper and error shape.
 * Every function in prompts.js and collections.js goes through request().
 */

// Only the dev server may fall back to the local backend. A production build
// without the variable would otherwise call localhost from the user's browser
// and fail with a misleading "can't reach the server".
const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  (import.meta.env.DEV ? 'http://localhost:8000' : undefined)

if (!BASE_URL) {
  throw new Error('VITE_API_BASE_URL is not set; see frontend/.env.example')
}

/**
 * A failed request, in one shape whatever went wrong.
 *
 * `status` is the HTTP status, or null when the server was never reached
 * (down, network failure, or blocked by CORS). `detail` is the API's
 * `detail` field when there is one: a string, or a list for a 422.
 */
export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === 'string' ? detail : `Request failed (${status ?? 'no response'})`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

/**
 * Send a request to the API and return its parsed JSON body.
 *
 * @param {string} path Path after the base URL, starting with "/".
 * @param {object} [options]
 * @param {string} [options.method] HTTP method; GET when absent.
 * @param {object} [options.body] Sent as JSON when present.
 * @returns {Promise<any>} The response body, or null for a 204.
 * @throws {ApiError} For a network failure or any status outside 200-299.
 */
export async function request(path, { method = 'GET', body } = {}) {
  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    // fetch rejects only when no response arrived; the browser hides the cause.
    throw new ApiError(null, null)
  }

  if (response.status === 204) {
    return null
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(response.status, data?.detail ?? null)
  }
  return data
}
