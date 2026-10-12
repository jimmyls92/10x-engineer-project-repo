# Frontend spec: PromptLab web app

| | |
|---|---|
| **Feature** | React frontend for PromptLab (Module 4, Task 4.1) |
| **Status** | Specified in Module 4 (Task 4.1); **built** in `frontend/` by Tasks 4.3-4.7. Line numbers cited below describe the backend at `58a31bf`; `backend/app/` has the current ones |
| **Decisions** | Worked through one at a time in Module 4's `docs/prompt-log.md` (branch `Week-4`), entries 11-37 |
| **Stack** | React with Vite, React Router, CSS Modules; the existing FastAPI backend in `backend/` |

The frontend is a client of the existing API only. It holds no data of its own: every screen
reads from the backend and reloads from it after each change.

---

## Scope

### In scope

The core journeys of criterion C3.3, and nothing else:

| Journey | Where |
|---|---|
| List prompts | Prompts screen |
| View a prompt's detail | Prompts screen, opened under its row |
| Create a prompt | Prompts screen, form window |
| Edit a prompt | Prompts screen, form window |
| Delete a prompt, with confirmation | Prompts screen, confirmation window |
| Search prompts | Prompts screen, search bar |
| Filter prompts by collection | Prompts screen, search bar |
| Manage collections (list, create, delete) | Collections screen |

### Out of scope

| Item | Why |
|---|---|
| **Tags** in the UI | Not a C3.3 journey (entries 12-13). The backend keeps supporting them. |
| **Prompt versions** in the UI | Not a C3.3 journey. Prompt Versioning is built on the backend only (Task 4.2). |
| **Renaming a collection** | The API has no endpoint for it; "manage collections" means create and delete. |

Although tags are not shown, **editing a prompt in the UI never removes its tags**: the edit sends
only the fields the form holds (`PATCH`), and the backend keeps any field it is not sent
(`api.py:237`). See *Which API endpoint each screen consumes*.

**No new endpoint is needed.** Every call below exists in `backend/app/api.py` today.

---

## Screens and their purpose

The app has **two screens, one per resource**, reached from two links in the header. **Prompts** is
the default screen. Both screens use **the same layout at every screen width**: a toolbar, then a
list. There is no separate phone layout (entry 21).

### Prompts screen (`/`)

**Purpose:** find, read, create, edit and delete prompts.

```
┌───────────────────────────────────────────────────────────┐
│ PromptLab                         Prompts | Collections   │  Header
├───────────────────────────────────────────────────────────┤
│ [Search......] [All collections ▾] [Apply] [Clear all]    │  SearchBar
│                                          [New prompt]     │
├───────────────────────────────────────────────────────────┤
│ Showing: collection Marketing, search "email"             │  status line
│ ▸ Prompt A                              [Edit] [Delete]   │
│ ▾ Prompt B                              [Edit] [Delete]   │
│     full detail of Prompt B                               │  PromptDetail
│ ▸ Prompt C                              [Edit] [Delete]   │
└───────────────────────────────────────────────────────────┘
```

| Element | Behaviour |
|---|---|
| **Search and collection filter** | A text box and a collection drop-down ("All collections" plus every collection). They take effect **only when Apply is pressed** (entry 18). Search matches a prompt's **title or description**, ignoring case; the prompt text itself is not searched (`utils.py:85`). |
| **Status line** | Above the list, always states the filter in force: "Showing all prompts", or e.g. "Showing: collection Marketing, search 'email'". It changes on Apply and on Clear all, never while the user types, so the user always knows what the list reflects. |
| **Clear all** | Empties both fields **and applies at once**: the list shows all prompts again (entry 19). |
| **List** | One row per prompt, newest first (the API's order), with the prompt's title and **Edit** and **Delete** buttons. |
| **Opening a prompt** | Clicking a row opens its full detail **underneath the row**, like a drop-down. **One prompt is open at a time**; clicking it again closes it. Apply, Clear all, and any reload of the list close it (entries 19, 21, 25). |
| **New prompt** | Opens the form window, empty. |
| **Edit** | Opens the form window, filled with that prompt. |
| **Delete** | Opens a confirmation window showing the prompt's details, with **Delete** and **Cancel** buttons (entries 26-27). |

**Form window** (create and edit) — a window floating over the screen (entry 23):

| Field | Rule (the API's own limits, `models.py:114-116`) |
|---|---|
| Title | Required, 1-200 characters |
| Content | Required |
| Description | Optional, up to 500 characters |
| Collection | Drop-down of existing collections plus "No collection" |

- **Save** checks the fields first. An invalid field is marked with a message under it, and nothing
  is sent until every field passes (entry 30).
- **After a successful save:** a success message appears, the window closes, and **the list reloads
  from the API with the filter still in force** (entry 25). If the saved prompt no longer matches
  the filter, it is not in the list; the status line says why.
- **Cancel** closes the window and **discards what was typed, without asking and without a
  message** (entry 25).
- **"No collection"** on edit sends `collection_id: null`, which takes the prompt out of its
  collection (`api.py:234-236`).

**After a successful delete:** a success message appears, the window closes, and the list reloads
with the filter in force.

### Collections screen (`/collections`)

**Purpose:** see, create and delete collections. It repeats the Prompts screen's pattern (entry 28).

```
┌───────────────────────────────────────────────────────────┐
│ PromptLab                         Prompts | Collections   │
├───────────────────────────────────────────────────────────┤
│                                      [New collection]     │
├───────────────────────────────────────────────────────────┤
│ Marketing — prompts for campaigns                [Delete] │
│ Engineering                                      [Delete] │
└───────────────────────────────────────────────────────────┘
```

| Element | Behaviour |
|---|---|
| **List** | One row per collection: name, description if any, and **Delete**. |
| **New collection** | Opens a form window with **Name** (required, 1-100 characters) and **Description** (optional, up to 500), the API's limits (`models.py:245-246`). Same Save, Cancel and success behaviour as the prompt form. |
| **Delete** | Opens a confirmation window, the same for every collection, empty or not: *"Deleting a collection will not delete its prompts. Its prompts will move to 'No collection'. To delete them, go to the Prompts screen."* with **Delete** and **Cancel** (entry 28). This matches the backend, which keeps the prompts and clears their `collection_id` (`api.py:366-392`). |

---

## Component inventory — each component, its responsibility and its props

Every component is its own module (`.jsx` file) with a CSS Module beside it when it has styles.
Screen components own the state and the API calls; every other component receives data and
callbacks through props.

### Layout

| Component | Responsibility | Props |
|---|---|---|
| `Layout` | Page frame: the header above the current screen | `children` |
| `Header` | App name, and links to the two screens with the current one marked | — |

### Prompts

| Component | Responsibility | Props |
|---|---|---|
| `PromptsPage` | The Prompts screen. Holds the applied filter, the prompt list, the collections, which prompt is open, which window is open and the success message; makes every API call of the screen | — |
| `SearchBar` | Search box, collection drop-down, Apply and Clear all. Keeps what the user types until Apply | `collections`, `onApply`, `onClear` |
| `PromptList` | Status line, then a `PromptCard` per prompt, or the empty-state message | `prompts`, `status`, `collections`, `appliedFilter`, `openId`, `onToggle`, `onEdit`, `onDelete`, `onCreate`, `onDetailError` |
| `PromptCard` | One row: title, Edit and Delete; renders `PromptDetail` underneath when open | `prompt`, `collections`, `isOpen`, `onToggle`, `onEdit`, `onDelete`, `onDetailError` |
| `PromptDetail` | Fetches the prompt by id and shows all its fields, with its own loading state; a failed fetch is reported through `onError` | `promptId`, `collections` (to name its collection), `onError` |
| `PromptForm` | Create and edit fields, field checks, and errors shown inside the form | `prompt` (absent when creating), `collections`, `onSave`, `onCancel`, `busy`, `error` |

### Collections

| Component | Responsibility | Props |
|---|---|---|
| `CollectionsPage` | The Collections screen. Holds the collection list, which window is open and the success message; makes every API call of the screen | — |
| `CollectionList` | A row per collection with Delete, or the loading, error or empty state | `collections`, `status`, `onDelete`, `onCreate` |
| `CollectionForm` | Name and description fields, field checks, errors inside the form | `onSave`, `onCancel`, `busy`, `error` |

### Shared

| Component | Responsibility | Props |
|---|---|---|
| `Button` | Every button, with a disabled state used while a request runs | `variant`, `type`, `disabled`, `onClick`, `children` |
| `Modal` | The floating window that hosts forms, confirmations and error pop-ups | `title`, `onClose`, `children` |
| `ConfirmDialog` | Delete / Cancel confirmation, used for prompts and collections; shows the item's details, the spinner while deleting and a failed delete | `title`, `message`, `children`, `onConfirm`, `onCancel`, `busy`, `error`, `resource` |
| `LoadingSpinner` | Spinning icon with a short label naming the operation | `label` |
| `ErrorMessage` | A plain-language error message with the status code underneath | `error`, `resource` ("prompt" or "collection") |
| `SuccessMessage` | Message confirming that a save or delete worked; disappears after 4 seconds or on its close button | `message`, `onClose` |

### Differences from the component list in Task 4.4

| Difference | Why |
|---|---|
| **`Sidebar` is not built** | Two screens need two links, which fit in `Header`; a sidebar would hold nothing else (entry 27). |
| **`PromptsPage` and `CollectionsPage` added** | One component per screen holds that screen's state and API calls, so the others stay presentational. |
| **`ConfirmDialog` added** | Both delete confirmations have the same shape. |
| **`SuccessMessage` added** | Save and delete both confirm success to the user (entries 24-26). |
| **`SearchBar` lives in `prompts/`, not shared** | It holds the collection filter, which only the Prompts screen has. |

---

## Which API endpoint each screen consumes

The functions are those named in Task 4.5, in `src/api/prompts.js` and `src/api/collections.js`.

### Prompts screen

| When | Function | Endpoint |
|---|---|---|
| Screen opens, Apply, Clear all, after a save or delete | `getPrompts(filter)` | `GET /prompts?search=…&collection_id=…` (empty values left out) |
| Screen opens (filter and form drop-downs) | `getCollections()` | `GET /collections` |
| A prompt is opened | `getPrompt(id)` | `GET /prompts/{id}` |
| Save in the form, creating | `createPrompt(data)` | `POST /prompts` |
| Save in the form, editing | `updatePrompt(id, data)` | `PATCH /prompts/{id}`, sending title, content, description and collection_id only |
| Delete confirmed | `deletePrompt(id)` | `DELETE /prompts/{id}` |

Opening a prompt fetches it again, rather than reusing the copy in the list, so the detail is
current when it is shown (entry 35).

**Why `updatePrompt` uses `PATCH`, not `PUT`:** `PUT` replaces the whole prompt, and a body without
`tags` clears them (`api.py:189`). The form has no tag field, so `PUT` would silently delete tags
set through the API. `PATCH` keeps every field it is not sent (entries 33-35).

### Collections screen

| When | Function | Endpoint |
|---|---|---|
| Screen opens, after a create or delete | `getCollections()` | `GET /collections` |
| Save in the form | `createCollection(data)` | `POST /collections` |
| Delete confirmed | `deleteCollection(id)` | `DELETE /collections/{id}` |

### Connection to the backend

`src/api/client.js` holds the base URL, read from the environment variable `VITE_API_BASE_URL`,
and one fetch wrapper used by every function. The wrapper turns every failure into one error shape,
with the HTTP status (none when the server was not reached), so screens handle errors the same way.

---

## State management approach

- **React's built-in state, kept in each screen component** (`PromptsPage`, `CollectionsPage`). No
  global store and no caching library: the two screens share nothing but the collection list, which
  each screen loads for itself (entry 35).
- **The backend is the only source of truth.** After every create, edit or delete, the screen
  reloads its list from the API instead of patching a local copy, so no cache can drift from the
  stored data (entries 24-25).
- **The applied filter is separate from what is typed.** `SearchBar` keeps the text and selection
  being typed; `PromptsPage` keeps the filter last applied, which drives the request and the status
  line.
- **The current screen lives in the URL** (`/` and `/collections`), through React Router, so the
  browser's back button and a page reload keep the user on their screen.

---

## Loading, error and empty state behaviour

### Loading

Every request shows a spinner with a short label naming the operation, **where its result will
appear** (entry 31):

| Request | Where | Label |
|---|---|---|
| Loading a list | In place of the list | "Loading prompts…", "Loading collections…" |
| Opening a prompt | Under its row, in place of the detail | "Loading prompt…" |
| Saving | Inside the form window | "Saving…" |
| Deleting | Inside the confirmation window | "Deleting…" |

**The buttons that started a request are disabled until it ends**, so a double click cannot send
it twice (entry 31).

### Errors

Every failed request produces a visible message; none is swallowed. The message is **plain
language, with the status code underneath** when there is one (entry 30):

| Case | Message | Code shown |
|---|---|---|
| Server not reached (down, network, or blocked by CORS) | "Can't reach the server. Check your connection and try again." | — |
| `404` — the prompt or collection no longer exists | "This prompt no longer exists." / "This collection no longer exists." The list reloads. | 404 |
| `400` — the chosen collection no longer exists | "The selected collection no longer exists. Choose another one." | 400 |
| `422` — input rejected | "Some fields were rejected. Check them and try again." | 422 |
| Any other status | "Something went wrong on the server. Try again." | the status |

**Where it appears:**

- **While a form or confirmation window is open**, the error is shown inside that window, and what
  the user typed is kept (entry 30).
- **Otherwise** (loading a list, opening a prompt) it appears in a pop-up window. If a list could
  not be loaded, the list area behind it reads "Prompts could not be loaded." (or "Collections…"),
  so the screen is never blank.

The form's own field checks catch empty or too-long fields before anything is sent, so a `422`
should only reach the user when the client and server rules disagree.

### Success messages

After a save or delete, a success message appears above the list. **It disappears by itself after
4 seconds**, or sooner with its close button; a new message replaces the previous one, and screen
readers announce it (entries 47-48).

### Empty states

| Case | Message | Button |
|---|---|---|
| No prompts exist, no filter applied | "No prompts yet." | New prompt |
| A filter is applied and matches nothing | "No prompts match this filter." | none: Clear all and the status line are already in view (entry 33) |
| No collections exist | "No collections yet." | New collection |

---

## Folder structure

**Organizing principle: code is grouped by feature — layout, prompts, collections and shared
components — with every API call kept in `api/`.**

```
frontend/
├── .env.example              VITE_API_BASE_URL
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.jsx              mounts the app
    ├── App.jsx               the router and the two routes
    ├── index.css             global styles
    ├── api/
    │   ├── client.js
    │   ├── prompts.js
    │   └── collections.js
    └── components/
        ├── layout/           Layout, Header
        ├── prompts/          PromptsPage, SearchBar, PromptList, PromptCard, PromptDetail, PromptForm
        ├── collections/      CollectionsPage, CollectionList, CollectionForm
        └── shared/           Button, Modal, ConfirmDialog, LoadingSpinner, ErrorMessage, SuccessMessage
```

Each component sits beside its CSS Module (`PromptCard.jsx`, `PromptCard.module.css`). Vite
template files that this structure does not use (`src/assets/`, `App.css`, the sample logos) are
removed in Task 4.3. The backend stays in `backend/`; the frontend only talks to it over HTTP.

**Styling:** CSS Modules, which Vite supports with no extra dependency and which scope each
component's styles to that component.
