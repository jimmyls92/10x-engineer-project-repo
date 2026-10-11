import Button from '../shared/Button.jsx'
import LoadingSpinner from '../shared/LoadingSpinner.jsx'
import PromptCard from './PromptCard.jsx'
import styles from './PromptList.module.css'

/**
 * The sentence above the list stating the filter in force.
 *
 * @param {{search: string, collectionId: string}} filter
 * @param {object[]} collections Used to name the filtered collection.
 * @returns {string}
 */
function describeFilter(filter, collections) {
  const parts = []
  if (filter.collectionId) {
    const collection = collections.find((c) => c.id === filter.collectionId)
    parts.push(`collection ${collection ? collection.name : '(deleted collection)'}`)
  }
  if (filter.search) parts.push(`search "${filter.search}"`)
  return parts.length === 0 ? 'Showing all prompts' : `Showing: ${parts.join(', ')}`
}

/**
 * Status line, then a card per prompt, the loading state, the error state or
 * the empty-state message.
 *
 * @param {object} props
 * @param {object[]} props.prompts
 * @param {'loading'|'ready'|'error'} props.status State of the last list request.
 * @param {object[]} props.collections
 * @param {{search: string, collectionId: string}} props.appliedFilter
 * @param {string|null} props.openId The prompt open under its row, if any.
 * @param {(id: string) => void} props.onToggle
 * @param {(prompt: object) => void} props.onEdit
 * @param {(prompt: object) => void} props.onDelete
 * @param {() => void} props.onCreate Offered when no prompt exists yet.
 * @param {(error: Error) => void} props.onDetailError A prompt's detail failed to load.
 */
function PromptList({
  prompts,
  status,
  collections,
  appliedFilter,
  openId,
  onToggle,
  onEdit,
  onDelete,
  onCreate,
  onDetailError,
}) {
  const filtered = Boolean(appliedFilter.search || appliedFilter.collectionId)

  let body
  if (status === 'loading') {
    body = <LoadingSpinner label="Loading prompts…" />
  } else if (status === 'error') {
    body = <p className={styles.notice}>Prompts could not be loaded.</p>
  } else if (prompts.length === 0 && filtered) {
    body = <p className={styles.notice}>No prompts match this filter.</p>
  } else if (prompts.length === 0) {
    body = (
      <div className={styles.notice}>
        <p>No prompts yet.</p>
        <Button variant="primary" onClick={onCreate}>
          New prompt
        </Button>
      </div>
    )
  } else {
    body = (
      <ul className={styles.list}>
        {prompts.map((prompt) => (
          <PromptCard
            key={prompt.id}
            prompt={prompt}
            collections={collections}
            isOpen={prompt.id === openId}
            onToggle={() => onToggle(prompt.id)}
            onEdit={() => onEdit(prompt)}
            onDelete={() => onDelete(prompt)}
            onDetailError={onDetailError}
          />
        ))}
      </ul>
    )
  }

  return (
    <section aria-label="Prompts">
      <p className={styles.status}>{describeFilter(appliedFilter, collections)}</p>
      {body}
    </section>
  )
}

export default PromptList
