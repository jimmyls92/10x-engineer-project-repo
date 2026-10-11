import { useState } from 'react'
import Button from '../shared/Button.jsx'
import styles from './SearchBar.module.css'

/**
 * Search box, collection filter, Apply and Clear all.
 *
 * What the user types is kept here and only reaches the list on Apply (or
 * Enter), so the list never changes while typing (specs/frontend.md).
 *
 * @param {object} props
 * @param {object[]} props.collections The collections offered in the filter.
 * @param {(filter: {search: string, collectionId: string}) => void} props.onApply
 * @param {() => void} props.onClear Called after the fields are emptied.
 */
function SearchBar({ collections, onApply, onClear }) {
  const [search, setSearch] = useState('')
  const [collectionId, setCollectionId] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    onApply({ search: search.trim(), collectionId })
  }

  function handleClear() {
    setSearch('')
    setCollectionId('')
    onClear()
  }

  return (
    <form className={styles.bar} onSubmit={handleSubmit} role="search">
      <label className={styles.field}>
        <span className={styles.label}>Search title or description</span>
        <input type="search" value={search} onChange={(event) => setSearch(event.target.value)} />
      </label>
      <label className={styles.field}>
        <span className={styles.label}>Collection</span>
        <select value={collectionId} onChange={(event) => setCollectionId(event.target.value)}>
          <option value="">All collections</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </label>
      <div className={styles.actions}>
        <Button type="submit" variant="primary">
          Apply
        </Button>
        <Button onClick={handleClear}>Clear all</Button>
      </div>
    </form>
  )
}

export default SearchBar
