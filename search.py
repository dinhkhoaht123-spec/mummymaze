import characters
import heapq 

# --- SAFE GATE HANDLING ---
def check_key_position(character, gate, key_position):
    if gate and key_position and character.get_x() == key_position[0] and character.get_y() == key_position[1]:
        is_closed = gate.get("isClosed", False)
        gate["isClosed"] = not is_closed
    return gate

def update_list_character(list_character):
    i = 0
    while i < len(list_character):
        j = 0
        while j < len(list_character):
            if j != i and list_character[i].check_same_position(list_character[j]):
                del list_character[j]
            j += 1
        i += 1
    return list_character

def update_lists_character(list_strong, list_weak):
    for i in range(len(list_strong)):
        j = 0
        while j < len(list_weak):
            if list_strong[i].check_same_position(list_weak[j]):
                del list_weak[j]
            j += 1
    return list_weak

# --- FIX: Check list of traps ---
def check_explorer_is_killed(explorer, mw, mr, sw, sr, trap_list):
    # Check if explorer hits ANY trap
    if trap_list:
        for t in trap_list:
            if explorer.get_x() == t[0] and explorer.get_y() == t[1]:
                return True
                
    for l in [mw, mr, sw, sr]:
        for e in l:
            if explorer.get_x() == e.get_x() and explorer.get_y() == e.get_y(): return True
    return False

def attempt_move(explorer_x, explorer_y, explorer_tmp, mummy_white_tmp, mummy_red_tmp, scorpion_white_tmp, scorpion_red_tmp,
                 current_gate_tmp, key_position, trap_list, maze):
    explorer_is_killed = False
    explorer_tmp.move_xy(explorer_x, explorer_y)
    
    if key_position:
        current_gate_tmp = check_key_position(explorer_tmp, current_gate_tmp, key_position)
        
    # --- FIRST MOVE ---
    for i in range(len(mummy_white_tmp)): mummy_white_tmp[i] = mummy_white_tmp[i].white_move(maze, current_gate_tmp, explorer_tmp)
    if key_position:
        for m in mummy_white_tmp: current_gate_tmp = check_key_position(m, current_gate_tmp, key_position)
            
    for i in range(len(mummy_red_tmp)): mummy_red_tmp[i] = mummy_red_tmp[i].red_move(maze, current_gate_tmp, explorer_tmp)
    if key_position:
        for m in mummy_red_tmp: current_gate_tmp = check_key_position(m, current_gate_tmp, key_position)
            
    for i in range(len(scorpion_white_tmp)): scorpion_white_tmp[i] = scorpion_white_tmp[i].white_move(maze, current_gate_tmp, explorer_tmp)
    if key_position:
        for s in scorpion_white_tmp: current_gate_tmp = check_key_position(s, current_gate_tmp, key_position)
            
    for i in range(len(scorpion_red_tmp)): scorpion_red_tmp[i] = scorpion_red_tmp[i].red_move(maze, current_gate_tmp, explorer_tmp)
    if key_position:
        for s in scorpion_red_tmp: current_gate_tmp = check_key_position(s, current_gate_tmp, key_position)

    explorer_is_killed = check_explorer_is_killed(explorer_tmp, mummy_white_tmp, mummy_red_tmp, scorpion_white_tmp, scorpion_red_tmp, trap_list)

    if not explorer_is_killed:
        mummy_white_tmp = update_list_character(mummy_white_tmp)
        mummy_red_tmp = update_list_character(mummy_red_tmp)
        scorpion_white_tmp = update_list_character(scorpion_white_tmp)
        scorpion_red_tmp = update_list_character(scorpion_red_tmp)
        
        if mummy_red_tmp: mummy_red_tmp = update_lists_character(mummy_white_tmp, mummy_red_tmp)
        if scorpion_white_tmp: scorpion_white_tmp = update_lists_character(mummy_white_tmp, scorpion_white_tmp)
        if scorpion_red_tmp: scorpion_red_tmp = update_lists_character(mummy_white_tmp, scorpion_red_tmp)
        if scorpion_white_tmp: scorpion_white_tmp = update_lists_character(mummy_red_tmp, scorpion_white_tmp)
        if scorpion_red_tmp: scorpion_red_tmp = update_lists_character(mummy_red_tmp, scorpion_red_tmp)
        if scorpion_red_tmp: scorpion_red_tmp = update_lists_character(scorpion_white_tmp, scorpion_red_tmp)

    # --- SECOND MOVE ---
        for i in range(len(mummy_white_tmp)): mummy_white_tmp[i] = mummy_white_tmp[i].white_move(maze, current_gate_tmp, explorer_tmp)
        if key_position:
            for m in mummy_white_tmp: current_gate_tmp = check_key_position(m, current_gate_tmp, key_position)
            
        for i in range(len(mummy_red_tmp)): mummy_red_tmp[i] = mummy_red_tmp[i].red_move(maze, current_gate_tmp, explorer_tmp)
        if key_position:
            for m in mummy_red_tmp: current_gate_tmp = check_key_position(m, current_gate_tmp, key_position)
            
        mummy_white_tmp = update_list_character(mummy_white_tmp)
        mummy_red_tmp = update_list_character(mummy_red_tmp)
        
        if mummy_red_tmp: mummy_red_tmp = update_lists_character(mummy_white_tmp, mummy_red_tmp)
        if scorpion_white_tmp: scorpion_white_tmp = update_lists_character(mummy_white_tmp, scorpion_white_tmp)
        if scorpion_red_tmp: scorpion_red_tmp = update_lists_character(mummy_white_tmp, scorpion_red_tmp)
        if scorpion_white_tmp: scorpion_white_tmp = update_lists_character(mummy_red_tmp, scorpion_white_tmp)
        if scorpion_red_tmp: scorpion_red_tmp = update_lists_character(mummy_red_tmp, scorpion_red_tmp)
        
        explorer_is_killed = check_explorer_is_killed(explorer_tmp, mummy_white_tmp, mummy_red_tmp, scorpion_white_tmp, scorpion_red_tmp, trap_list)

    return explorer_is_killed

def get_state_key(exp, mw, mr, sw, sr, gate):
    mw_pos = tuple((m.get_x(), m.get_y()) for m in mw)
    mr_pos = tuple((m.get_x(), m.get_y()) for m in mr)
    sw_pos = tuple((s.get_x(), s.get_y()) for s in sw)
    sr_pos = tuple((s.get_x(), s.get_y()) for s in sr)
    g_closed = False
    if gate and isinstance(gate, dict):
        g_closed = gate.get('isClosed', False)
    return (exp.get_x(), exp.get_y(), mw_pos, mr_pos, sw_pos, sr_pos, g_closed)

def Dijkstra(explorer_char, mw_char, mr_char, sw_char, sr_char, gate, trap_list, key_pos, maze):
    pq = []
    counter = 0 
    
    path = [[explorer_char.get_x(), explorer_char.get_y()]]
    safe_gate = gate if gate else {}
    
    heapq.heappush(pq, (0, counter, path, explorer_char, mw_char, mr_char, sw_char, sr_char, safe_gate))
    
    visited = set()
    initial_key = get_state_key(explorer_char, mw_char, mr_char, sw_char, sr_char, safe_gate)
    visited.add(initial_key)

    while pq:
        cost, _, current_path, curr_exp, curr_mw, curr_mr, curr_sw, curr_sr, curr_gate = heapq.heappop(pq)
        ex, ey = curr_exp.get_x(), curr_exp.get_y()

        # Check Win (Standard)
        rows, cols = len(maze), len(maze[0])
        # Win if Standing on S
        if maze[ex][ey] == 'S': return current_path
        # Win if Adjacent to S
        if (ex > 0 and maze[ex-1][ey] == 'S') or \
           (ex < rows-1 and maze[ex+1][ey] == 'S') or \
           (ey > 0 and maze[ex][ey-1] == 'S') or \
           (ey < cols-1 and maze[ex][ey+1] == 'S'):
            return current_path

        moves = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        
        for dx, dy in moves:
            nx, ny = ex + dx, ey + dy
            if not (0 <= nx < rows and 0 <= ny < cols): continue

            temp_exp = characters.Explorer(ex, ey)
            if temp_exp.eligible_character_move(maze, curr_gate, ex, ey, nx, ny):
                
                next_exp = characters.Explorer(nx, ny)
                next_mw = [characters.mummy_white(m.get_x(), m.get_y()) for m in curr_mw]
                next_mr = [characters.mummy_red(m.get_x(), m.get_y()) for m in curr_mr]
                next_sw = [characters.scorpion_white(s.get_x(), s.get_y()) for s in curr_sw]
                next_sr = [characters.scorpion_red(s.get_x(), s.get_y()) for s in curr_sr]
                next_gate = curr_gate.copy() if curr_gate else {}

                is_dead = attempt_move(nx, ny, next_exp, next_mw, next_mr, next_sw, next_sr, next_gate, key_pos, trap_list, maze)
                
                if not is_dead:
                    state_key = get_state_key(next_exp, next_mw, next_mr, next_sw, next_sr, next_gate)
                    if state_key not in visited:
                        visited.add(state_key)
                        counter += 1
                        new_path = current_path + [[next_exp.get_x(), next_exp.get_y()]]
                        heapq.heappush(pq, (cost + 1, counter, new_path, next_exp, next_mw, next_mr, next_sw, next_sr, next_gate))

    return None