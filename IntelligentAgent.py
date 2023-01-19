# IntelligentAgent
import time

# Constant for infinity
inf = float('inf')

# Maximum search depth
max_depth_overall = 100

# Maximum time allowed
max_time_allowed = 0.15

class IntelligentAgent(BaseAI):
	def __init__(self):
		self.max_time = 0

	def getMove(self, grid):
		# Initialize time limit
		self.max_time = time.process_time() + max_time_allowed
		
		# Default move of DOWN
		move = 1

		# Iterate through the different depth levels
		for max_d in range(max_depth_overall):
			# Maximize for the current depth
			maxChild, _ = self.maximize(grid, -inf, inf, 0, max_d)
			
			# Time check and update maximum
			if time.process_time() > self.max_time: break
			elif maxChild != None: move = maxChild
		
		return move	
	
	def maximize(self, grid, alpha, beta, depth, max_depth):
		# Check time and depth limit
		if time.process_time() > self.max_time: return None, -inf
		if depth > max_depth: return None, self.heuristic(grid)
		
		# Start maximization search
		maxChild, maxUtility = None, -inf

		for child, child_grid in grid.getAvailableMoves():
			# Get utility for the child grid, based on 90% chance of getting a 2 and 
			# 10% chance of getting a 4
			utility = 0.9 * self.minimize(child_grid, alpha, beta, depth+1, max_depth, 2) + \
			   0.1 * self.minimize(child_grid, alpha, beta, depth+1, max_depth, 4)

			# Check if a new maximum has been found
			if utility > maxUtility:
				# Update to the new maximum
				maxChild, maxUtility = child, utility

				# Alpha-beta pruning
				if maxUtility >= beta: break
				if maxUtility > alpha: alpha = maxUtility
		
		# Done
		return maxChild, maxUtility
	
	def minimize(self, grid, alpha, beta, depth, max_depth, tile):
		# Check time and depth limit
		if time.process_time() > self.max_time: return inf
		if depth > max_depth: return self.heuristic(grid)

		# Start minimization search
		minUtility = inf

		for cell in grid.getAvailableCells():
			# Create a child grid with the new tile value and find its utility
			child_grid = grid.clone()
			child_grid.setCellValue(cell, tile)
			_ , utility = self.maximize(child_grid, alpha, beta, depth+1, max_depth)

			# Check if a new minimum has been found
			if utility < minUtility:
				# Update to the new minimum
				minUtility = utility

				# Alpha-beta pruning
				if minUtility <= alpha: break
				if minUtility < beta: beta = minUtility
		
		# Done
		return minUtility

	def heuristic(self, grid):
		"""
		The heuristic used here consists of a weighted score of the following five 
		components (higher is better in all cases):
		- Emptiness (E, 40%): the percentage of empty cells in the grid
		- Monotonicity (M, 35%): the percentage of rows and columns that are 
		   monotonically increasing in the same direction
		- Smoothness (S, 35%): the percentage of non-empty cells that have 
		   identically valued neighbors below and/or to the right (having both 
			 counts double)
		- Highest tile value (H, 5%): assessed on a logarithmic scale relative 
		   to 4096 (if the highest tile value is V, then H = log2(V)/log(4096))
		- If the highest tile is in a corner (C, 5%): 1 if the highest tile value
		   is in a corner, 0 otherwise
		"""
		# Loop over the grid to make some measurements for the components
		empty_cells = 0
		mono_LR, mono_RL, mono_UD, mono_DU = 0, 0, 0, 0
		smooth_count, smooth_total = 0, 0
		highest_tile = 0
		
		# Loop over the rows
		for i in range(grid.size):
			# Check if row i is monotonically increasing from left to right
			if grid.getCellValue((i,0)) <= grid.getCellValue((i,1)) \
	 			and grid.getCellValue((i,1)) <= grid.getCellValue((i,2)) \
				and grid.getCellValue((i,2)) <= grid.getCellValue((i,3)):
				mono_LR += 1

			# Check if row i is monotonically increasing from right to left
			if grid.getCellValue((i,0)) >= grid.getCellValue((i,1)) \
	 			and grid.getCellValue((i,1)) >= grid.getCellValue((i,2)) \
				and grid.getCellValue((i,2)) >= grid.getCellValue((i,3)):
				mono_RL += 1

			# Check if column i is monotonically increasing from top to bottom
			if grid.getCellValue((0,i)) <= grid.getCellValue((1,i)) \
				and grid.getCellValue((1,i)) <= grid.getCellValue((2,i)) \
				and grid.getCellValue((2,i)) <= grid.getCellValue((3,i)):
				mono_UD += 1

			# Check if column i is monotonically increasing from bottom to top
			if grid.getCellValue((0,i)) >= grid.getCellValue((1,i)) \
				and grid.getCellValue((1,i)) >= grid.getCellValue((2,i)) \
				and grid.getCellValue((2,i)) >= grid.getCellValue((3,i)):
				mono_DU += 1

			for j in range(grid.size):
				# Get the calue of the current cell
				current_cell = grid.getCellValue((i, j))

				# Update the highest tile value
				if current_cell > highest_tile: highest_tile = current_cell
				
				# Is the current cell empty?
				if current_cell == 0:
					# Cell is empty, increment the empty cells counter
					empty_cells += 1
				else:
					# Cell is not empty
					
					# Check if the cell to the right (if there is one) is the same
					if j < grid.size-1:
						smooth_total += 1
						if grid.getCellValue((i, j+1)) == current_cell:
							smooth_count += 1

					# Check if the cell below (if there is one) is the same
					if i < grid.size-1:
						smooth_total += 1
						if grid.getCellValue((i+1, j)) == current_cell:
							smooth_count += 1

		# Emptiness
		E = float(empty_cells) / 15

		# Monotonicity
		M = float(max(mono_LR, mono_RL) + max(mono_UD, mono_DU)) / 8

		# Smoothness
		S = float(smooth_count) / smooth_total if smooth_total != 0 else 0

		# Highest tile value
		H = math.log2(highest_tile) / math.log2(4096)

		# If the highest tile is in a corner
		C = 0
		for corner in [(0,0), (0,3), (3,0), (3,3)]:
			if grid.getCellValue(corner) == highest_tile:
				C = 1
				break
		
		# Compute the heuristic from the five components and return
		return 0.4*E + 0.35*M + 0.35*S + 0.05*H + 0.05*C