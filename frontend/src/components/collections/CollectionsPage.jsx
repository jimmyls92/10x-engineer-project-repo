import { useCallback, useEffect, useRef, useState } from 'react'
import { createCollection, deleteCollection, getCollections } from '../../api/collections.js'
import Button from '../shared/Button.jsx'
import ConfirmDialog from '../shared/ConfirmDialog.jsx'
import ErrorMessage from '../shared/ErrorMessage.jsx'
import Modal from '../shared/Modal.jsx'
import SuccessMessage from '../shared/SuccessMessage.jsx'
import CollectionForm from './CollectionForm.jsx'
import CollectionList from './CollectionList.jsx'
import styles from './CollectionsPage.module.css'

// The wording agreed for every collection delete, empty or not (specs/frontend.md).
const DELETE_MESSAGE =
  "Deleting a collection will not delete its prompts. Its prompts will move to 'No collection'. " +
  'To delete them, go to the Prompts screen.'

/**
 * The Collections screen (specs/frontend.md). Holds the screen's state and
 * makes every API call; like the Prompts screen, it reloads the list from the
 * API after each create or delete instead of patching it locally.
 */
function CollectionsPage() {
  const [collections, setCollections] = useState([])
  const [listStatus, setListStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  // The one window open at a time: { kind: 'create' | 'delete', collection? }.
  const [activeWindow, setActiveWindow] = useState(null)
  const [busy, setBusy] = useState(false)
  const [windowError, setWindowError] = useState(null)
  const [popupError, setPopupError] = useState(null)
  const [success, setSuccess] = useState(null) // { id, message }

  // Numbers each list request, so an older response cannot overwrite a newer one.
  const latestRequest = useRef(0)

  // Fetch the list into state. The initial state is already "loading", so the
  // first load calls this directly.
  const fetchCollections = useCallback(() => {
    const requestId = ++latestRequest.current
    return getCollections()
      .then((data) => {
        if (requestId !== latestRequest.current) return
        setCollections(data.collections)
        setListStatus('ready')
      })
      .catch((error) => {
        if (requestId !== latestRequest.current) return
        setListStatus('error')
        setPopupError(error)
      })
  }, [])

  function loadCollections() {
    setListStatus('loading')
    fetchCollections()
  }

  useEffect(() => {
    fetchCollections()
  }, [fetchCollections])

  const clearSuccess = useCallback(() => setSuccess(null), [])

  function openWindow(kind, collection) {
    setWindowError(null)
    setActiveWindow({ kind, collection })
  }

  function closeWindow() {
    setActiveWindow(null)
    setWindowError(null)
  }

  async function saveCollection(data) {
    setBusy(true)
    setWindowError(null)
    try {
      await createCollection(data)
      setSuccess({ id: Date.now(), message: 'Collection created.' })
      closeWindow()
      loadCollections()
    } catch (error) {
      setWindowError(error)
    } finally {
      setBusy(false)
    }
  }

  async function confirmDelete() {
    setBusy(true)
    setWindowError(null)
    try {
      await deleteCollection(activeWindow.collection.id)
      setSuccess({ id: Date.now(), message: 'Collection deleted.' })
      closeWindow()
      loadCollections()
    } catch (error) {
      setWindowError(error)
      // Deleted elsewhere: reload so the list stops showing it.
      if (error.status === 404) loadCollections()
    } finally {
      setBusy(false)
    }
  }

  const deleting = activeWindow?.kind === 'delete' ? activeWindow.collection : null

  return (
    <>
      <div className={styles.toolbar}>
        <h1 className={styles.heading}>Collections</h1>
        <Button variant="primary" onClick={() => openWindow('create')}>
          New collection
        </Button>
      </div>

      {success && <SuccessMessage key={success.id} message={success.message} onClose={clearSuccess} />}

      <CollectionList
        collections={collections}
        status={listStatus}
        onDelete={(collection) => openWindow('delete', collection)}
        onCreate={() => openWindow('create')}
      />

      {activeWindow?.kind === 'create' && (
        <Modal title="New collection" onClose={busy ? () => {} : closeWindow}>
          <CollectionForm onSave={saveCollection} onCancel={closeWindow} busy={busy} error={windowError} />
        </Modal>
      )}

      {deleting && (
        <ConfirmDialog
          title={`Delete "${deleting.name}"`}
          message={DELETE_MESSAGE}
          onConfirm={confirmDelete}
          onCancel={closeWindow}
          busy={busy}
          error={windowError}
          resource="collection"
        />
      )}

      {popupError && (
        <Modal title="Something went wrong" onClose={() => setPopupError(null)}>
          <ErrorMessage error={popupError} resource="collection" />
          <div className={styles.popupActions}>
            <Button onClick={() => setPopupError(null)}>Close</Button>
          </div>
        </Modal>
      )}
    </>
  )
}

export default CollectionsPage
