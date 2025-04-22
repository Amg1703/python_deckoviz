import json

prompts = [
    "A solitary tree standing tall against a raging storm, its branches bending but not breaking, symbolizing the resilience of the human spirit in the face of adversity.",
    "A phoenix rising from the ashes, its wings ablaze with vibrant colors, representing the power of rebirth and renewal after facing challenges.",
    "A wounded warrior standing tall on a battlefield, their eyes filled with determination and unwavering courage.",
    "A climber scaling a steep mountain face, their every step a testament to their perseverance and unwavering spirit.",
    "A vast starry sky ablaze with the Milky Way, inspiring a sense of awe and wonder at the immensity of the universe.",
    "A breathtaking aurora borealis shimmering across the night sky, its ethereal colors and dancing patterns evoking a sense of wonder and enchantment.",
    "A majestic waterfall cascading down a lush green mountainside, its thunderous roar and misty spray creating a sense of awe and reverence for nature.",
    "A vibrant coral reef teeming with colorful fish and intricate formations, revealing the hidden beauty and wonder of the underwater world.",
    "A tranquil lake reflecting a vibrant sunset, its calm waters mirroring the serenity of the sky and creating a peaceful atmosphere.",
    "A Japanese zen garden with meticulously raked sand, moss-covered rocks, and a tranquil pond, inviting contemplation and inner peace.",
    "A lone figure meditating under a majestic tree, their body radiating calmness and serenity in harmony with nature.",
    "A peaceful meadow bathed in soft morning light, with dewdrops glistening on blades of grass and birds singing in the trees, evoking a sense of tranquility and well-being.",
]


def store_prompts_to_json(prompts, filename="prompts.json"):
    with open(filename, "w") as file:
        json.dump(prompts, file, indent=4)


store_prompts_to_json(prompts)
print(len(prompts))
