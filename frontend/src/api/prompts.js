/** Prompt endpoints, as listed in specs/frontend.md. */
import { request } from './client.js'

/**
 * List prompts, newest first.
 *
 * @param {object} [filter]
 * @param {string} [filter.search] Text to find in title or description.
 * @param {string} [filter.collectionId] Keep only this collection's prompts.
 * @returns {Promise<{prompts: object[], total: number}>}
 */
export function getPrompts({ search, collectionId } = {}) {
  const params = new URLSearchParams()
  // Empty values are left out; the API ignores them anyway.
  if (search) params.set('search', search)
  if (collectionId) params.set('collection_id', collectionId)
  const query = params.toString()
  return request(query ? `/prompts?${query}` : '/prompts')
}

/** @param {string} id @returns {Promise<object>} The prompt. */
export function getPrompt(id) {
  return request(`/prompts/${encodeURIComponent(id)}`)
}

/**
 * @param {{title: string, content: string, description?: string, collection_id?: string|null}} data
 * @returns {Promise<object>} The created prompt.
 */
export function createPrompt(data) {
  return request('/prompts', { method: 'POST', body: data })
}

/**
 * Update a prompt with the form's fields.
 *
 * PATCH, not PUT: PUT clears the tags when the body leaves them out, and the
 * form has no tag field (specs/frontend.md, api.py:189).
 *
 * @param {string} id
 * @param {{title: string, content: string, description: string|null, collection_id: string|null}} data
 * @returns {Promise<object>} The updated prompt.
 */
export function updatePrompt(id, data) {
  return request(`/prompts/${encodeURIComponent(id)}`, { method: 'PATCH', body: data })
}

/** @param {string} id @returns {Promise<null>} */
export function deletePrompt(id) {
  return request(`/prompts/${encodeURIComponent(id)}`, { method: 'DELETE' })
}
