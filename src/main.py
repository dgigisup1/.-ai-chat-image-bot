"""Simple CLI for the AI chatbot scaffold.

Usage examples:
  python -m src.main chat --message "Hello"
  python -m src.main code --prompt "Write a fizzbuzz in python"
  python -m src.main image --prompt "photorealistic cat"  # requires provider/key
"""
import argparse
import sys
from .ai_chatbot import AIChatBot


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ai-chat-bot")
    sub = parser.add_subparsers(dest="cmd")

    p_chat = sub.add_parser("chat")
    p_chat.add_argument("--message", required=True)
    p_chat.add_argument("--persona", required=False, help="Optional persona/system prompt to use for this chat")

    p_code = sub.add_parser("code")
    p_code.add_argument("--prompt", required=True)
    p_code.add_argument("--lang", required=False)

    p_image = sub.add_parser("image")
    p_image.add_argument("--prompt", required=True)
    p_image.add_argument("--size", required=False, default="512x512", help="Image size (e.g. 256x256, 512x512, 1024x1024)")
    p_image.add_argument("--output", required=False, default="output.png", help="Output image filename")

    p_video = sub.add_parser("video")
    p_video.add_argument("--prompt", required=True)
    p_video.add_argument("--duration", type=int, default=4)
    p_video.add_argument("--output", required=False, default="output.mp4", help="Output video filename")
    p_video.add_argument("--yes", action="store_true", help="Skip confirmation for potentially expensive video generation")

    args = parser.parse_args(argv)
    # Persona argument overrides environment variable AI_PERSONA
    persona = getattr(args, "persona", None) or None
    bot = AIChatBot(persona=persona)

    try:
        if args.cmd == "chat":
            out = bot.chat(args.message)
            print(out)
        elif args.cmd == "code":
            out = bot.generate_code(args.prompt, language_hint=args.lang)
            print(out)
        elif args.cmd == "image":
            size = args.size
            img_bytes = bot.generate_image(args.prompt, size=size)
            # Save to file
            out_path = args.output
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            print(f"Wrote {out_path}")
        elif args.cmd == "video":
            # Confirm if the video will make many frames (costly)
            duration = args.duration
            # Use the same fps default as AIChatBot
            fps = 6
            total_frames = max(1, int(fps * duration))
            if total_frames > 12 and not getattr(args, "yes", False):
                confirm = input(f"This will generate {total_frames} images via your image provider (may incur cost). Continue? [y/N]: ")
                if confirm.strip().lower() not in ("y", "yes"):
                    print("Cancelled video generation.")
                    return
            vid = bot.generate_video(args.prompt, duration_seconds=duration)
            out_path = args.output
            with open(out_path, "wb") as f:
                f.write(vid)
            print(f"Wrote {out_path}")
        else:
            parser.print_help()
    except Exception as e:
        print("Error:", e)
        sys.exit(2)


if __name__ == "__main__":
    main()
