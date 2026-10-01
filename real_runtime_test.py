import asyncio
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

async def test_readonly():
    config = LocalAgentConfig(
        system_instructions="You are an assistant. Do NOT execute any bash commands or modify any files. Return 'SUCCESS: ' followed by a summary of the root directory.",
        capabilities=CapabilitiesConfig()  # empty = read-only normally
    )
    
    async with Agent(config) as agent:
        response = await agent.chat("Inspect the repository structure. Do not create, modify, delete, or execute anything. Return a concise summary.")
        print(f"Agent reply: {response.text}")
        
async def test_write():
    config = LocalAgentConfig(
        system_instructions="Create a file named orchai_runtime_test.txt containing exactly: OrchAI runtime test",
        capabilities=CapabilitiesConfig(
            edit_file=True,
            run_command=False
        )
    )
    async with Agent(config) as agent:
        response = await agent.chat("Create the file.")
        print(f"Agent reply: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_readonly())
    print("\n---\n")
    asyncio.run(test_write())
