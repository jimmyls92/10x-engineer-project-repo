/** Collection endpoints, as listed in specs/frontend.md. */
import { request } from './client.js'

/** @returns {Promise<{collections: object[], total: number}>} */
export function getCollections() {
  return request('/collections')
}

/**
 * @param {{name: string, description?: string}} data
 * @returns {Promise<object>} The created collection.
 */
export function createCollection(data) {
  return request('/collections', { method: 'POST', body: data })
}

/**
 * Delete a collection. The API keeps its prompts and unfiles them.
 *
 * @param {string} id
 * @returns {Promise<null>}
 */
export function deleteCollection(id) {
  return request(`/collections/${encodeURIComponent(id)}`, { method: 'DELETE' })
}
