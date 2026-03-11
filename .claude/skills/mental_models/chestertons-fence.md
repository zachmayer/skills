# Chesterton's Fence

Before removing something, understand why it was put there. If you don't understand its purpose, you don't understand the consequences of removing it.

## The Principle

"There exists in such a case a certain institution or law; let us say, for the sake of simplicity, a fence or gate erected across a road. The more modern type of reformer goes gaily up to it and says, 'I don't see the use of this; let us clear it away.' To which the more intelligent type of reformer will do well to answer: 'If you don't see the use of it, I certainly won't let you clear it away. Go away and think. Then, when you can come back and tell me that you do see the use of it, I may allow you to destroy it.'"

## Application

- **Code:** Before deleting "dead" code, understand why it exists. It may handle an edge case you haven't encountered.
- **Process:** Before eliminating a process step, understand what problem it solved originally.
- **Architecture:** Before removing a component, understand all its consumers and interactions.
- **Policy:** Before changing a rule, understand what failure mode it prevents.

## The Test

Can you explain why this exists? If yes, you can make an informed decision about removing it. If no, investigate before changing anything.
