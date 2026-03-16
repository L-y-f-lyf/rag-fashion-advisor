with open('check.log', 'w', encoding='utf-8') as f:
    f.write("Starting...\n")

    try:
        from langchain_core.agents import AgentExecutor
        f.write("OK: langchain_core.agents.AgentExecutor\n")
    except Exception as e:
        f.write(f"FAIL: langchain_core.agents.AgentExecutor - {e}\n")

    try:
        from langchain.agents import AgentExecutor
        f.write("OK: langchain.agents.AgentExecutor\n")
    except Exception as e:
        f.write(f"FAIL: langchain.agents.AgentExecutor - {e}\n")

    try:
        from langchain.agents import create_react_agent
        f.write("OK: langchain.agents.create_react_agent\n")
    except Exception as e:
        f.write(f"FAIL: langchain.agents.create_react_agent - {e}\n")

    try:
        import agent
        f.write("OK: agent module\n")
    except Exception as e:
        f.write(f"FAIL: agent module - {e}\n")
        import traceback
        f.write(traceback.format_exc())
