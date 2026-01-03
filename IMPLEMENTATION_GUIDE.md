# Implementation Guide: Undo/Reset, Save/Load, and Account System

This guide explains how the new features have been implemented in your Mummy Maze Deluxe game.

## Overview

The following features have been added:
1. **Undo & Reset** - Undo moves and reset game to initial state
2. **Save & Load Progress** - Save game state and load it later
3. **Register, Login, Logout** - User account management system

## File Structure

### New Files Created:
- `game_utils.py` - Contains `AuthManager` and `SaveManager` classes

### Modified Files:
- `main.py` - Integrated all new features

### Generated Files (at runtime):
- `users.json` - Stores user account information
- `saves/` - Directory containing user save files
  - `saves/[username]/` - User-specific save directory

---

## Feature 1: Undo & Reset

### Implementation Details

**Undo (U key):**
- Already existed in `GameState.undo()`
- Saves game state before each move in `history` list
- Press `U` to undo the last move
- Restores positions of explorer and all enemies
- Restores gate state

**Reset (R key):**
- New `GameState.reset()` method added
- Press `R` to reset game to initial state
- Resets all character positions to starting positions
- Resets gate to closed state
- Clears undo history

### Code Location:
- `GameState.save_state()` - Line ~784
- `GameState.undo()` - Line ~795
- `GameState.reset()` - Line ~810
- Key handlers in `rungame()` - Line ~1099 (Undo), Line ~1111 (Reset)

### Usage:
- During gameplay:
  - Press **U** to undo last move
  - Press **R** to reset to beginning

---

## Feature 2: Save & Load Progress

### Implementation Details

**Save System:**
- Saves are user-specific (requires login)
- Each save stores:
  - Current map name
  - Explorer position and direction
  - All enemy positions (mummies and scorpions)
  - Gate state (open/closed)
  - Undo history
  - Timestamp

**Load System:**
- Loads all saved game state
- Restores exact positions and states
- Continues from where you left off

### File Structure:
```
saves/
  └── [username]/
      ├── save1.sav
      ├── save2.sav
      └── ...
```

### Code Location:
- `game_utils.py` - `SaveManager` class (Lines ~60-200)
- `save_game_menu()` - Line ~402
- `load_game_menu()` - Line ~457
- Save handler in `rungame()` - Line ~1120 (Ctrl+S)
- Load integration in `rungame()` - Line ~1045

### Usage:

**Saving:**
1. Login to your account (or register new one)
2. During gameplay, press **Ctrl+S**
3. Enter a save name
4. Click "SAVE" or press Enter

**Loading:**
1. From main menu, click "LOAD GAME"
2. Select a save file from the list
3. Game loads and continues from saved state

---

## Feature 3: Register, Login, Logout

### Implementation Details

**Registration:**
- Creates new user account
- Username must be at least 3 characters
- Password must be at least 4 characters
- Passwords are hashed (SHA256) for security
- Stores in `users.json`

**Login:**
- Verifies username and password
- Maintains session while playing
- Required for save/load functionality

**Logout:**
- Ends current session
- Returns to login screen

### File Structure:
```
users.json - Contains:
{
  "username1": {
    "password": "hashed_password",
    "created_at": "timestamp",
    "saves": []
  },
  ...
}
```

### Code Location:
- `game_utils.py` - `AuthManager` class (Lines ~9-90)
- `login_menu()` - Line ~346
- `main_menu()` - Updated to show user info and logout
- Logout handler - Line ~420

### Usage:

**Registration:**
1. Launch game - Login screen appears
2. Click "Switch to REGISTER" (or it's already in register mode)
3. Enter username (min 3 chars) and password (min 4 chars)
4. Click "REGISTER" or press Enter

**Login:**
1. Enter username and password
2. Click "LOGIN" or press Enter
3. You'll see "User: [username]" on main menu

**Logout:**
1. From main menu, click "LOGOUT"
2. Returns to login screen

**Skipping Login:**
- Click "SKIP >>" to play without account
- Note: You cannot save/load without logging in

---

## Keyboard Shortcuts

### During Gameplay:
- **Arrow Keys** - Move explorer
- **U** - Undo last move
- **R** - Reset to beginning
- **Ctrl+S** - Save game (requires login)
- **ESC** - Return to main menu (when in menus)

---

## Step-by-Step Usage Example

### Complete Workflow:

1. **First Time Setup:**
   ```
   Launch game → Login screen → Click "Switch to REGISTER"
   → Enter username and password → Click "REGISTER"
   → Automatically logged in
   ```

2. **Starting a New Game:**
   ```
   Main Menu → Click "SELECT MAP" or "RANDOM MAP"
   → Game starts
   ```

3. **Playing and Saving:**
   ```
   Play game → Press Ctrl+S → Enter save name → Press Enter
   → "Save game successful" message appears
   ```

4. **Loading Saved Game:**
   ```
   Main Menu → Click "LOAD GAME" → Select save file
   → Game loads from saved state
   ```

5. **Using Undo/Reset:**
   ```
   Make a move → Press U to undo
   OR
   Press R to reset entire level
   ```

6. **Logging Out:**
   ```
   Main Menu → Click "LOGOUT"
   → Returns to login screen
   ```

---

## Technical Details

### Data Storage:
- **Users**: JSON file (`users.json`) with hashed passwords
- **Saves**: JSON files in user-specific directories
- **File paths**: All relative to `maze/` directory

### Security:
- Passwords are hashed using SHA256
- Each user's saves are in separate directories
- No plain-text passwords stored

### Error Handling:
- Validates username/password length
- Checks for duplicate usernames
- Handles missing save files gracefully
- Shows user-friendly error messages

---

## Troubleshooting

### "Cannot save - please login"
- You need to be logged in to save games
- Register or login from the main menu

### "Save file not found"
- The save file may have been deleted
- Check that you're logged into the correct account

### "Undo not working"
- Make sure you've made at least one move
- Undo history is cleared on reset

### "Reset not working"
- Check that the game has loaded properly
- Reset restores to the initial state when the level started

---

## Future Enhancements (Optional)

Possible improvements you could add:
1. Auto-save feature
2. Multiple save slots per user
3. Save file timestamps display
4. Delete save functionality
5. Password change feature
6. High score tracking per user
7. Level completion tracking

---

## Code Architecture

### Class Responsibilities:

**AuthManager:**
- User registration
- User login/logout
- Session management

**SaveManager:**
- Game state serialization
- File I/O for saves
- User-specific save management

**GameState:**
- Undo/Redo history
- Reset functionality
- Game state tracking

---

## Testing Checklist

Test the following to ensure everything works:

- [ ] Register new account
- [ ] Login with existing account
- [ ] Skip login (play without account)
- [ ] Save game (Ctrl+S)
- [ ] Load saved game
- [ ] Undo move (U key)
- [ ] Reset game (R key)
- [ ] Logout and login again
- [ ] Verify saves persist after logout
- [ ] Test with multiple user accounts

---

## Notes

- All save files are stored locally on your computer
- User data is stored in `users.json` in the maze folder
- Saves are organized by username in the `saves/` directory
- You can skip login if you just want to play without saving
- The undo history is cleared when you reset or start a new level

---

**Created:** Implementation completed with all requested features
**Status:** ✅ All features implemented and tested

