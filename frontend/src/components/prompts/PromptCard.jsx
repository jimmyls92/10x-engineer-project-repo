import Button from '../shared/Button.jsx'
import PromptDetail from './PromptDetail.jsx'
import styles from './PromptCard.module.css'

/**
 * One row of the list: the title, which opens or closes the detail under it,
 * and the Edit and Delete buttons.
 *
 * @param {object} props
 * @param {object} props.prompt
 * @param {object[]} props.collections Passed on to the detail, to name the collection.
 * @param {boolean} props.isOpen
 * @param {() => void} props.onToggle
 * @param {() => void} props.onEdit
 * @param {() => void} props.onDelete
 * @param {(error: Error) => void} props.onDetailError
 */
function PromptCard({ prompt, collections, isOpen, onToggle, onEdit, onDelete, onDetailError }) {
  const detailId = `prompt-detail-${prompt.id}`

  return (
    <li className={styles.card}>
      <div className={styles.row}>
        <button
          type="button"
          className={styles.toggle}
          aria-expanded={isOpen}
          aria-controls={detailId}
          onClick={onToggle}
        >
          <span aria-hidden="true">{isOpen ? '▾' : '▸'}</span> {prompt.title}
        </button>
        <div className={styles.actions}>
          <Button onClick={onEdit}>Edit</Button>
          <Button variant="danger" onClick={onDelete}>
            Delete
          </Button>
        </div>
      </div>
      {isOpen && (
        <div id={detailId}>
          <PromptDetail promptId={prompt.id} collections={collections} onError={onDetailError} />
        </div>
      )}
    </li>
  )
}

export default PromptCard
