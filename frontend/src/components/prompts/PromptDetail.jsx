import { useEffect, useState } from 'react'
import { getPrompt } from '../../api/prompts.js'
import LoadingSpinner from '../shared/LoadingSpinner.jsx'
import styles from './PromptDetail.module.css'

/**
 * Format an API timestamp for display. The API sends naive UTC timestamps
 * (no offset), so "Z" is added before the browser converts them to local time.
 *
 * @param {string} value
 * @returns {string}
 */
function formatTime(value) {
  return new Date(`${value}Z`).toLocaleString()
}

/**
 * Fetches one prompt and shows all its fields. It fetches again rather than
 * reusing the list's copy, so what it shows is current (specs/frontend.md).
 *
 * @param {object} props
 * @param {string} props.promptId
 * @param {object[]} props.collections Used to name the prompt's collection.
 * @param {(error: Error) => void} props.onError A failed fetch is reported to the screen.
 */
function PromptDetail({ promptId, collections, onError }) {
  const [prompt, setPrompt] = useState(null)

  useEffect(() => {
    // Closing the row before the response arrives must not update a removed component.
    let active = true
    getPrompt(promptId)
      .then((data) => {
        if (active) setPrompt(data)
      })
      .catch((error) => {
        if (active) onError(error)
      })
    return () => {
      active = false
    }
  }, [promptId, onError])

  if (!prompt) {
    return <LoadingSpinner label="Loading prompt…" />
  }

  const collection = collections.find((c) => c.id === prompt.collection_id)

  return (
    <dl className={styles.detail}>
      <dt>Content</dt>
      <dd className={styles.content}>{prompt.content}</dd>
      <dt>Description</dt>
      <dd>{prompt.description || '—'}</dd>
      <dt>Collection</dt>
      <dd>{collection ? collection.name : 'No collection'}</dd>
      <dt>Created</dt>
      <dd>{formatTime(prompt.created_at)}</dd>
      <dt>Updated</dt>
      <dd>{formatTime(prompt.updated_at)}</dd>
    </dl>
  )
}

export default PromptDetail
