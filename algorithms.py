import math
import heapq

def a_star(start, target, obstacles, width, height):
    grid_size = 20 #breaks the whole screen into small 20x20 grids
    start_node = (int(start[0]//grid_size)*grid_size, int(start[1]//grid_size)*grid_size)#stores current location. of plane
    target_node = (int(target[0]//grid_size)*grid_size, int(target[1]//grid_size)*grid_size)#stores target location. of plane
    
    open_set = []#list of those point which are currently being checked by algorithm 
    heapq.heappush(open_set, (0, start_node))#here priority queue is used ,it finds that point first whose f(n)valev is the least 
   
    came_from = {}
    g_score = {start_node: 0}
    
    while open_set:#executes as long as it doesnt gets it desired path and all options are not over
        current = heapq.heappop(open_set)[1]

        if math.dist(current, target_node) < grid_size * 1.0:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        # 8 Directions for smooth movement
        for dx, dy in [(0, grid_size), (grid_size, 0), (0, -grid_size), (-grid_size, 0),
                       (grid_size, grid_size), (-grid_size, -grid_size), (grid_size, -grid_size), (-grid_size, grid_size)]:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if 0 <= neighbor[0] <= width and 0 <= neighbor[1] <= height:
                blocked = False
                for ox, oy, orad in obstacles:# collisions avoidance-checks if plane is at safe distance from storm or not
                    if math.dist(neighbor, (ox, oy)) < orad + 15:  #buffer distance 15 unit
                        blocked = True
                        break
                if blocked: continue

                temp_g = g_score[current] + math.dist(current, neighbor)#g(n)
                if neighbor not in g_score or temp_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = temp_g
                    f_score = temp_g + math.dist(neighbor, target_node)#f(n) = g(n) + h(n) 
                    heapq.heappush(open_set, (f_score, neighbor))
                    
                    #ye line Priority Queue implement karti hai. Hum f_score ko heappush karte hain taaki algorithm hamesha us
                    #point ko pehle explore kare jo destination ke sabse kareeb aur sabse saste raste par ho. Isse rasta dhoondne ki speed badh jaati h               
    return None