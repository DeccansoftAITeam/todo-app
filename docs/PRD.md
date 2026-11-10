# PRD: To-Do Web App (v1)

## Goal

Give an individual a simple web app to capture, prioritize and track to-dos, with a clear view of what is overdue. The app is the running example for a training course, so v1 stays deliberately small and easy to build and test.

**Key constraint:** v1 has no persistence. To-dos live in memory only, and refreshing or closing the page clears them.

## Users

Individuals and members of small teams who manage their own task list. Each session belongs to one person. There are no accounts, roles or shared lists.

## User stories

**1. Create a to-do.** As a user, I want to add a to-do so I can capture a task quickly.
- Title is required. A blank or whitespace-only title is rejected with a visible message.
- Due date is optional and is a calendar date only, with no time.
- Category is one of work, personal, shopping or other. The default is other.
- Priority is one of low, medium or high. The default is medium.
- A new to-do starts open and not archived, and it appears in the list immediately.

**2. List my to-dos.** As a user, I want to see my to-dos so I know what's on my plate.
- By default, the main list shows every to-do that isn't archived, both open and completed.
- Each item shows its title, completion status, due date (if set), category and priority.
- When there are no to-dos to show, the list shows an empty-state message.

**3. Mark a to-do complete or incomplete.** As a user, I want to tick off finished work and undo mistakes.
- One control toggles a to-do between open and completed.
- Completed items look visually different from open items.
- Toggling never archives the to-do or changes any other field.

**4. Archive a to-do.** As a user, I want to clear finished or irrelevant to-dos without losing them.
- Archiving hides the to-do from the main list and the Overdue view.
- The main list has a "Show archived" filter, which is off by default.
- When the filter is on, archived to-dos appear in the list and are visually marked as archived.
- When the filter is off, no archived to-dos are shown.
- The app has no delete action anywhere.

**5. Restore an archived to-do.** As a user, I want to bring back something I archived by mistake.
- Archived to-dos shown by the filter have a Restore action.
- A restored to-do stays visible when the filter is turned off, and its completion status and all other fields are unchanged.

**6. See overdue to-dos.** As a user, I want a view of what's late so I can act on it.
- A to-do is overdue when its due date is before today (user's local date), it is open, and it is not archived.
- To-dos due today are not overdue.
- To-dos with no due date are never overdue.
- The Overdue view shows only overdue to-dos and has an empty state when there are none.

**7. Search by title.** As a user, I want to find a to-do by its title.
- Typing in the search box filters the visible list to to-dos whose title contains the search text, ignoring case.
- Clearing the search box restores the full list.
- When nothing matches, a no-results message appears.

## Out of scope (v1)

- Sharing or collaboration, and multiple users
- Login and accounts
- Mobile app (the web app only)
- Notifications and reminders
- Persistence of any kind: local storage, server or database
- Editing a to-do's fields after creation
- Deleting to-dos
- Custom categories or priorities

## Open questions

1. Should search also apply to the Overdue view and to archived to-dos when "Show archived" is on?
2. What is the default sort order of the main list, for example by due date, by priority or by creation order? What about the Overdue view?
3. Is filtering by category or priority required, or are those fields display-only in v1?
4. Is there a maximum title length?
5. Should completed to-dos stay in the main list, or move to the bottom or into their own section?
6. Which browsers must be supported?
7. When persistence comes later, where should data live, and what happens to the "one person per account" assumption without login?