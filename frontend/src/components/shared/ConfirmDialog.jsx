import Button from './Button.jsx'
import ErrorMessage from './ErrorMessage.jsx'
import LoadingSpinner from './LoadingSpinner.jsx'
import Modal from './Modal.jsx'
import styles from './ConfirmDialog.module.css'

/**
 * Delete / Cancel confirmation, for prompts and collections.
 *
 * While the delete runs, the spinner shows and both buttons are disabled; if
 * it fails, the error is shown here rather than in a second window.
 *
 * @param {object} props
 * @param {string} props.title Heading of the window.
 * @param {string} props.message What deleting will do.
 * @param {React.ReactNode} [props.children] Details of the item, shown under the message.
 * @param {() => void} props.onConfirm Called by Delete.
 * @param {() => void} props.onCancel Called by Cancel and by Escape.
 * @param {boolean} [props.busy] True while the delete request runs.
 * @param {import('../../api/client.js').ApiError|null} [props.error] The failed delete, if any.
 * @param {'prompt'|'collection'} props.resource What is being deleted, for the error message.
 */
function ConfirmDialog({ title, message, children, onConfirm, onCancel, busy = false, error = null, resource }) {
  // Escape is ignored while the request runs, like the disabled Cancel button.
  const close = busy ? () => {} : onCancel

  return (
    <Modal title={title} onClose={close}>
      <p>{message}</p>
      {children}
      {error && <ErrorMessage error={error} resource={resource} />}
      {busy && <LoadingSpinner label="Deleting…" />}
      <div className={styles.actions}>
        <Button onClick={onCancel} disabled={busy}>
          Cancel
        </Button>
        <Button variant="danger" onClick={onConfirm} disabled={busy}>
          Delete
        </Button>
      </div>
    </Modal>
  )
}

export default ConfirmDialog
