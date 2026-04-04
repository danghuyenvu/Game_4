# Monte Carlo Bot for Splendor

## How It Works

The Monte Carlo algorithm evaluates each possible action by:

1. **Generating all valid actions** from the current game state
2. **Simulating each action** N times (default: 100 simulations)
3. **Running random playouts** - playing out the rest of the game with random moves
4. **Calculating average score gain** for each action
5. **Selecting the action** with the highest expected score gain

## Core Components

### 1. `get_action(cards, bank, players)`
Main entry point that returns the best action as a tuple:
- `("BUY", card)` - Purchase a card
- `("RESERVE", card)` - Reserve a card (gains gold)
- `("TAKE_3", [i, j, k])` - Take 3 different gems
- `("TAKE_2", i)` - Take 2 of the same gem type

### 2. `_simulate_action(action, cards, bank, players)`
Runs N simulations for a single action:
- Copies game state (players + bank)
- Executes the action
- Plays out the rest randomly
- Returns average score improvement

### 3. `_playout(players, current_player_idx, bank, cards)`
Simulates random gameplay from current state:
- Each player takes a random valid action
- Continues for up to 50 turns
- Returns final score

## Usage in Your Game

```python
from monte_carlo import Monte_carlo

# Create Monte Carlo bot with 100 simulations per action
bot = Monte_carlo(num_simulations=100)

# Get the best action
action = bot.get_action(cards_on_board, bank, all_players)

if action:
    action_type, action_data = action
    # Execute action in your game logic
```

## Tuning Parameters

### Number of Simulations
- **Lower (50)**: Fast, less accurate, good for real-time
- **Default (100)**: Balanced accuracy and speed
- **Higher (500+)**: Very accurate but slow

Change in initialization:
```python
bot = Monte_carlo(num_simulations=500)
```

## Strategy Insights

The bot learns to:
- **Buy valuable cards** early (high point cards)
- **Reserve cards** to gain gold and secure good deals
- **Manage gem economy** - not hoarding too many gems
- **Block opponents** by reserving cards they might buy
- **Adapt to game state** through simulations

## Performance Tips

1. **Cache simulations** if running multiple bots
2. **Reduce simulations** in early game, increase late game
3. **Use threading** for parallel simulations (future enhancement)
4. **Profile** to find bottleneck actions

## Potential Improvements

1. **Alpha-Beta Pruning** - Eliminate bad actions early
2. **Heuristic Evaluation** - Add domain knowledge scoring
3. **Transposition Tables** - Cache known positions
4. **Upper Confidence Bounds (UCB)** - Balance exploration/exploitation
5. **Parallel Simulations** - ThreadPoolExecutor for speed

## Debugging

Check `bot.action_values` dict to see scoring for each action:
```python
action = bot.get_action(cards, bank, players)
print(bot.action_values)  # {"('BUY', card1)": 2.5, ...}
```
