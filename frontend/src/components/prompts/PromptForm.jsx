import { useState } from 'react'
import Button from '../shared/Button.jsx'
import ErrorMessage from '../shared/ErrorMessage.jsx'
import LoadingSpinner from '../shared/LoadingSpinner.jsx'
import styles from './PromptForm.module.css'

// The API's own limits (models.py:114-116), checked before anything is sent.
const TITLE_MAX = 200
const DESCRIPTION_MAX = 500

/**
 * Check the fields and return a message per invalid field.
 *
 * @param {{title: string, content: string, description: string}} values
 * @returns {Record<string, string>} Empty when every field passes.
 */
function validate(values) {
  const errors = {}
  if (!values.title.trim()) errors.title = 'Title is required.'
  else if (values.title.length > TITLE_MAX) errors.title = `Title must be ${TITLE_MAX} characters or fewer.`
  if (!values.content.trim()) errors.content = 'Content is required.'
  if (values.description.length > DESCRIPTION_MAX) {
    errors.description = `Description must be ${DESCRIPTION_MAX} characters or fewer.`
  }
  return errors
}

/**
 * Create and edit form for a prompt, shown inside a Modal.
 *
 * What was typed stays in this component, so a failed save keeps it; the
 * error is shown here rather than in a second window (specs/frontend.md).
 *
 * @param {object} props
 * @param {object} [props.prompt] The prompt being edited; absent when creating.
 * @param {object[]} props.collections Offered in the collection drop-down.
 * @param {(data: object) => void} props.onSave Receives the fields to send.
 * @param {() => void} props.onCancel
 * @param {boolean} props.busy True while the save request runs.
 * @param {Error|null} props.error The failed save, if any.
 */
function PromptForm({ prompt, collections, onSave, onCancel, busy, error }) {
  const [values, setValues] = useState({
    title: prompt?.title ?? '',
    content: prompt?.content ?? '',
    description: prompt?.description ?? '',
    collectionId: prompt?.collection_id ?? '',
  })
  const [fieldErrors, setFieldErrors] = useState({})

  function update(field) {
    return (event) => setValues((current) => ({ ...current, [field]: event.target.value }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    const errors = validate(values)
    setFieldErrors(errors)
    if (Object.keys(errors).length > 0) return

    // Exactly the form's fields: never tags, so an edit (PATCH) keeps them.
    // An empty description or "No collection" is sent as null, which clears it.
    onSave({
      title: values.title,
      content: values.content,
      description: values.description || null,
      collection_id: values.collectionId || null,
    })
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit} noValidate>
      <label className={styles.field}>
        <span>Title</span>
        <input
          value={values.title}
          onChange={update('title')}
          aria-invalid={Boolean(fieldErrors.title)}
          aria-describedby={fieldErrors.title ? 'title-error' : undefined}
        />
        {fieldErrors.title && <span id="title-error" className={styles.fieldError}>{fieldErrors.title}</span>}
      </label>

      <label className={styles.field}>
        <span>Content</span>
        <textarea
          rows={6}
          value={values.content}
          onChange={update('content')}
          aria-invalid={Boolean(fieldErrors.content)}
          aria-describedby={fieldErrors.content ? 'content-error' : undefined}
        />
        {fieldErrors.content && <span id="content-error" className={styles.fieldError}>{fieldErrors.content}</span>}
      </label>

      <label className={styles.field}>
        <span>Description (optional)</span>
        <input
          value={values.description}
          onChange={update('description')}
          aria-invalid={Boolean(fieldErrors.description)}
          aria-describedby={fieldErrors.description ? 'description-error' : undefined}
        />
        {fieldErrors.description && (
          <span id="description-error" className={styles.fieldError}>{fieldErrors.description}</span>
        )}
      </label>

      <label className={styles.field}>
        <span>Collection</span>
        <select value={values.collectionId} onChange={update('collectionId')}>
          <option value="">No collection</option>
          {collections.map((collection) => (
            <option key={collection.id} value={collection.id}>
              {collection.name}
            </option>
          ))}
        </select>
      </label>

      {error && <ErrorMessage error={error} resource="prompt" />}
      {busy && <LoadingSpinner label="Saving…" />}

      <div className={styles.actions}>
        <Button onClick={onCancel} disabled={busy}>
          Cancel
        </Button>
        <Button type="submit" variant="primary" disabled={busy}>
          Save
        </Button>
      </div>
    </form>
  )
}

export default PromptForm
