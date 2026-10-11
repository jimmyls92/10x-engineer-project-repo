import { useCallback, useEffect, useRef, useState } from 'react'
import { getCollections } from '../../api/collections.js'
import { createPrompt, deletePrompt, getPrompts, updatePrompt } from '../../api/prompts.js'
import Button from '../shared/Button.jsx'
import ConfirmDialog from '../shared/ConfirmDialog.jsx'
import ErrorMessage from '../shared/ErrorMessage.jsx'
import Modal from '../shared/Modal.jsx'
import SuccessMessage from '../shared/SuccessMessage.jsx'
import PromptForm from './PromptForm.jsx'
import PromptList from './PromptList.jsx'
import SearchBar from './SearchBar.jsx'
import styles from './PromptsPage.module.css'

const NO_FILTER = { search: '', collectionId: '' }

/**
 * The Prompts screen (specs/frontend.md). Holds the screen's state and makes
 * every API call; the components below it only display and report clicks.
 *
 * The backend is the only source of truth: after each save or delete the list
 * is fetched again with the filter in force, never patched locally.
 */
function PromptsPage() {
  const [collections, setCollections] = useState([])
  const [appliedFilter, setAppliedFilter] = useState(NO_FILTER)
  const [prompts, setPrompts] = useState([])
  const [listStatus, setListStatus] = useState('loading') // 'loading' | 'ready' | 'error'
  const [openId, setOpenId] = useState(null)
  // The one window open at a time: { kind: 'create' | 'edit' | 'delete', prompt? }.
  const [activeWindow, setActiveWindow] = useState(null)
  const [busy, setBusy] = useState(false)
  const [windowError, setWindowError] = useState(null)
  // An error raised outside any window, shown in its own pop-up: { error, resource }.
  const [popupError, setPopupError] = useState(null)
  const [success, setSuccess] = useState(null) // { id, message }

  // Numbers each list request, so a slow response to an older Apply cannot
  // overwrite the list of a newer one.
  const latestRequest = useRef(0)

  // Fetch the list into state. The initial state is already "loading" with
  // nothing open, so the first load calls this directly.
  const fetchPrompts = useCallback((filter) => {
    const requestId = ++latestRequest.current
    return getPrompts(filter)
      .then((data) => {
        if (requestId !== latestRequest.current) return
        setPrompts(data.prompts)
        setListStatus('ready')
      })
      .catch((error) => {
        if (requestId !== latestRequest.current) return
        setListStatus('error')
        setPopupError({ error, resource: 'prompt' })
      })
  }, [])

  // Reload the list: show the spinner, close any open prompt, then fetch.
  const loadPrompts = useCallback(
    (filter) => {
      setListStatus('loading')
      setOpenId(null)
      fetchPrompts(filter)
    },
    [fetchPrompts],
  )

  useEffect(() => {
    fetchPrompts(NO_FILTER)
    getCollections()
      .then((data) => setCollections(data.collections))
      .catch((error) => setPopupError({ error, resource: 'collection' }))
  }, [fetchPrompts])

  const clearSuccess = useCallback(() => setSuccess(null), [])

  function showSuccess(message) {
    setSuccess({ id: Date.now(), message })
  }

  function applyFilter(filter) {
    setAppliedFilter(filter)
    loadPrompts(filter)
  }

  function clearFilter() {
    applyFilter(NO_FILTER)
  }

  function openWindow(kind, prompt) {
    setWindowError(null)
    setActiveWindow({ kind, prompt })
  }

  function closeWindow() {
    setActiveWindow(null)
    setWindowError(null)
  }

  // A 404 means the prompt was deleted elsewhere: the list is reloaded so it
  // stops showing it, while the error stays visible in the open window.
  function handleWindowError(error) {
    setWindowError(error)
    if (error.status === 404) loadPrompts(appliedFilter)
  }

  async function savePrompt(data) {
    setBusy(true)
    setWindowError(null)
    try {
      if (activeWindow.kind === 'edit') {
        await updatePrompt(activeWindow.prompt.id, data)
        showSuccess('Prompt saved.')
      } else {
        await createPrompt(data)
        showSuccess('Prompt created.')
      }
      closeWindow()
      loadPrompts(appliedFilter)
    } catch (error) {
      handleWindowError(error)
    } finally {
      setBusy(false)
    }
  }

  async function confirmDelete() {
    setBusy(true)
    setWindowError(null)
    try {
      await deletePrompt(activeWindow.prompt.id)
      showSuccess('Prompt deleted.')
      closeWindow()
      loadPrompts(appliedFilter)
    } catch (error) {
      handleWindowError(error)
    } finally {
      setBusy(false)
    }
  }

  // Kept stable across renders: PromptDetail fetches again whenever this
  // changes, and a new function on every render would refetch in a loop once
  // the error pop-up itself causes a render.
  const handleDetailError = useCallback(
    (error) => {
      setPopupError({ error, resource: 'prompt' })
      if (error.status === 404) loadPrompts(appliedFilter)
    },
    [appliedFilter, loadPrompts],
  )

  const deleting = activeWindow?.kind === 'delete' ? activeWindow.prompt : null

  return (
    <>
      <h1 className={styles.heading}>Prompts</h1>

      <div className={styles.toolbar}>
        <SearchBar collections={collections} onApply={applyFilter} onClear={clearFilter} />
        <Button variant="primary" onClick={() => openWindow('create')}>
          New prompt
        </Button>
      </div>

      {success && <SuccessMessage key={success.id} message={success.message} onClose={clearSuccess} />}

      <PromptList
        prompts={prompts}
        status={listStatus}
        collections={collections}
        appliedFilter={appliedFilter}
        openId={openId}
        onToggle={(id) => setOpenId((current) => (current === id ? null : id))}
        onEdit={(prompt) => openWindow('edit', prompt)}
        onDelete={(prompt) => openWindow('delete', prompt)}
        onCreate={() => openWindow('create')}
        onDetailError={handleDetailError}
      />

      {(activeWindow?.kind === 'create' || activeWindow?.kind === 'edit') && (
        <Modal
          title={activeWindow.kind === 'edit' ? 'Edit prompt' : 'New prompt'}
          onClose={busy ? () => {} : closeWindow}
        >
          <PromptForm
            prompt={activeWindow.prompt}
            collections={collections}
            onSave={savePrompt}
            onCancel={closeWindow}
            busy={busy}
            error={windowError}
          />
        </Modal>
      )}

      {deleting && (
        <ConfirmDialog
          title="Delete prompt"
          message="This prompt will be deleted permanently."
          onConfirm={confirmDelete}
          onCancel={closeWindow}
          busy={busy}
          error={windowError}
          resource="prompt"
        >
          <dl className={styles.details}>
            <dt>Title</dt>
            <dd>{deleting.title}</dd>
            {deleting.description && (
              <>
                <dt>Description</dt>
                <dd>{deleting.description}</dd>
              </>
            )}
            <dt>Content</dt>
            <dd className={styles.content}>{deleting.content}</dd>
          </dl>
        </ConfirmDialog>
      )}

      {popupError && (
        <Modal title="Something went wrong" onClose={() => setPopupError(null)}>
          <ErrorMessage error={popupError.error} resource={popupError.resource} />
          <div className={styles.popupActions}>
            <Button onClick={() => setPopupError(null)}>Close</Button>
          </div>
        </Modal>
      )}
    </>
  )
}

export default PromptsPage
