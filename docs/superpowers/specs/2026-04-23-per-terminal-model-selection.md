# Design Doc: Per-Terminal Model Selection

## Goal
Implement a model selection mechanism specific to each terminal pane in the GUI. This allows users to run different Gemini models in different workspace slots simultaneously.

## Context
Currently, model selection is global in the `MainWindow` header bar. Changing it attempts to restart the "active" session, which is not ideal for a multiplexed environment.

## Requirements
- Each `TerminalPane` must have its own header bar.
- The header bar must include a model selection button (dropdown/menu).
- The header bar must include the "Maximize" (Focus Mode) button, moved from the current overlay position.
- Changing the model in a terminal must restart only that specific terminal's process with the new model.
- The UI should be compact to remain usable in a grid of multiple terminals.

## Architecture & UI
### `TerminalPane` Structure
- `Gtk.Box` (Vertical)
    - `HeaderBar` (Custom Widget)
        - Start: `Gtk.Label` (Optional: current model name)
        - End: `Gtk.MenuButton` (Model selection)
        - End: `zoom_button` (Moved from overlay)
    - `Gtk.Overlay`
        - `Vte.Terminal`
        - `Adw.Banner` (Errors)

### Model Selection
- The `Gtk.MenuButton` will open a popover or menu listing available models.
- Available models will be retrieved from the `ConfigManager`.

### State Management
- `TerminalPane` will store its currently selected model.
- A signal `model-changed` will be emitted when a new model is selected.
- `MainWindow` will listen to this signal and call `process_manager.restart_with_model`.

## Testing Strategy
- Unit test for `TerminalPane` to verify header bar creation and button existence.
- Integration test to verify that clicking a model in the dropdown triggers the correct process restart.
- Test that multiple terminals can have different models selected.
