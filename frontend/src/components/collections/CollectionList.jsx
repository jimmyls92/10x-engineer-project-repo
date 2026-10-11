import Button from '../shared/Button.jsx'
import LoadingSpinner from '../shared/LoadingSpinner.jsx'
import styles from './CollectionList.module.css'

/**
 * A row per collection with its Delete button, or the loading, error or
 * empty state.
 *
 * @param {object} props
 * @param {object[]} props.collections
 * @param {'loading'|'ready'|'error'} props.status State of the last list request.
 * @param {(collection: object) => void} props.onDelete
 * @param {() => void} props.onCreate Offered when no collection exists yet.
 */
function CollectionList({ collections, status, onDelete, onCreate }) {
  if (status === 'loading') {
    return <LoadingSpinner label="Loading collections…" />
  }
  if (status === 'error') {
    return <p className={styles.notice}>Collections could not be loaded.</p>
  }
  if (collections.length === 0) {
    return (
      <div className={styles.notice}>
        <p>No collections yet.</p>
        <Button variant="primary" onClick={onCreate}>
          New collection
        </Button>
      </div>
    )
  }

  return (
    <ul className={styles.list} aria-label="Collections">
      {collections.map((collection) => (
        <li key={collection.id} className={styles.row}>
          <div className={styles.text}>
            <span className={styles.name}>{collection.name}</span>
            {collection.description && <span className={styles.description}>{collection.description}</span>}
          </div>
          <Button variant="danger" onClick={() => onDelete(collection)}>
            Delete
          </Button>
        </li>
      ))}
    </ul>
  )
}

export default CollectionList
