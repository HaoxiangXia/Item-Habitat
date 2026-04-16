# Agents Documentation

This document describes the specialized agents available for this warehouse management system project.

## Language Guidelines
- ✅ **所有代理必须使用中文与用户进行交流**
- ✅ 所有回复、说明、文档、注释统一使用简体中文
- ✅ 技术术语可保留英文原文，但必须提供中文解释
- ❌ 禁止全程使用英文回复用户
- ❌ 禁止中英混合无意义切换

---

## Available Agents

### general
- **Purpose**: General-purpose agent for researching complex questions and executing multi-step tasks
- **Tools**: Full access to all available tools
- **Use cases**:
  - Complex research tasks
  - Multi-step workflows
  - Code generation and refactoring
  - File exploration and analysis

### explore
- **Purpose**: Fast agent specialized for exploring codebases
- **Tools**: Optimized for file discovery and content analysis
- **Use cases**:
  - Finding files by patterns (e.g., `src/components/**/*.tsx`)
  - Searching code for keywords
  - Answering questions about codebase structure
  - Quick exploration of large codebases

## Agent Usage Guidelines

### When to Use Agents
- **Complex tasks**: Use agents for tasks requiring 3+ distinct steps
- **Research tasks**: When you need to gather information from multiple sources
- **Code exploration**: For understanding large codebases or finding specific patterns
- **Multi-file operations**: When changes span multiple files

### Agent Performance Notes
- Agents work autonomously once given clear instructions
- Provide detailed task descriptions for best results
- Specify expected output format in your prompt
- Use task IDs to continue multi-step conversations

## Recent Agent Activities

### UI Redesign Project
- **Agent**: general
- **Task**: Complete UI redesign with aurora glassmorphism theme
- **Files modified**:
  - `static/style.css` (complete rewrite with new design system)
  - `templates/layout.html` (sidebar navigation + aurora background)
  - `templates/index.html` (function cards with animations)
  - `templates/inbound.html` (glass form + modal updates)
  - `templates/outbound.html` (glass form + info card)
  - `templates/search.html` (filter form + results table)
  - `templates/history.html` (transaction history table)
  - `templates/location_stats.html` (statistics table)
  - `templates/location_detail.html` (detail view)
  - `static/main.js` (mobile interactions + animations)

### Codebase Exploration
- **Agent**: explore
- **Task**: Project structure analysis for UI redesign
- **Findings**: Flask + Jinja2 architecture, existing templates and static files identified

## Agent Command Patterns

### Starting Tasks
```
Task(description="Brief task description", prompt="Detailed instructions for agent", subagent_type="general")
```

### Continuing Tasks
```
Task(description="Continue previous work", prompt="Additional instructions", subagent_type="general", task_id="previous_task_id")
```

## Performance Tips

1. **Be specific**: Provide clear, detailed instructions
2. **Break down complex tasks**: Use multiple agent calls for different phases
3. **Specify output format**: Tell agents what format you expect results in
4. **Use appropriate agent**: Choose `explore` for discovery, `general` for execution
5. **Document agent usage**: Update this file after significant agent activities