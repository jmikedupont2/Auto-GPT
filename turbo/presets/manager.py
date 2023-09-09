from pathlib import Path

from colorama import Fore

from autogpt.app.utils import clean_input
from autogpt.logs import logger

SETTINGS_FILE = "ai.yaml"
PROMPTS_FILE = "prompts.yaml"
PRESETS_DIR = Path(__file__).parent.parent.parent / "config" / "presets"

class PresetManager:
    _presets = None

    @classmethod
    def get_all(cls) -> list[str]:
        if cls._presets is None:
            ai_files = PRESETS_DIR.glob(f"**/{SETTINGS_FILE}")
            prompt_files = PRESETS_DIR.glob(f"**/{PROMPTS_FILE}")
            dirs = set(
                [file.parent.relative_to(PRESETS_DIR) for file in ai_files]
                + [file.parent.relative_to(PRESETS_DIR) for file in prompt_files]
            )
            cls._presets = [".".join(dir.parts) for dir in dirs]
            cls._presets.sort()
        return cls._presets

    @classmethod
    def list(cls) -> None:
        presets = cls.get_all()
        count = len(presets)

        logger.typewriter_log("\n")
        logger.typewriter_log(
            f"{count} PRESET{'S' if count > 1 else ''} FOUND: ", Fore.CYAN
        )
        logger.typewriter_log("================================", Fore.CYAN)

        for i, preset in enumerate(presets, 1):
            logger.typewriter_log(f"  [{i}] - {preset}", Fore.CYAN)

    @classmethod
    def prompt_user(cls, config) -> None:
        cls.list()
        logger.typewriter_log("\n")
        preset = clean_input(
            config,
            f"{Fore.CYAN}Enter the number of the preset you want to use, or press Enter to skip: ",
            talk=False,
        )

        if preset:
            try:
                preset = int(preset)
                if preset > 0 and preset <= len(cls.get_all()):
                    preset_name = cls.get_all()[preset - 1]
                    logger.typewriter_log(f"Loading preset '{preset_name}'.", Fore.CYAN)
                    return cls.load(preset_name)
            except ValueError:
                logger.typewriter_log(
                    f"Preset '{preset}' not found. Skiping...",
                    Fore.RED,
                )
        return None, None

    @classmethod
    def validate(cls, preset_name: str) -> bool:
        if preset_name not in cls.get_all():
            logger.typewriter_log(
                f"Preset '{preset_name}' not found. Use '--presets' to see available presets.",
                Fore.RED,
            )
            return False
        return True

    @classmethod
    def load(cls, preset_name: str) -> tuple[str | None, str | None]:
        if cls.validate(preset_name):
            ai_settings_file = (
                Path(__file__).parent / preset_name.replace(".", "/") / SETTINGS_FILE
            )

            if ai_settings_file.exists():
                ai_settings = str(ai_settings_file)
                logger.typewriter_log(
                    f"Loading ai settings presets for '{preset_name}'.", Fore.CYAN
                )
            else:
                ai_settings = None
                logger.typewriter_log(
                    f"Preset '{preset_name}' does not have ai settings.",
                    Fore.YELLOW,
                )

            prompt_settings = cls.load_prompts(preset_name)
            cls.display_intro(preset_name)
            return ai_settings, prompt_settings
        return None, None

    @classmethod
    def display_intro(cls, preset_name: str) -> None | str:
        intro_file = Path(__file__).parent / preset_name.replace(".", "/") / "intro.md"

        if intro_file.exists():
            intro = intro_file.read_text()

        from pytimedinput import timedKey

        intro = (
            f"{Fore.CYAN}"
            "\n================================================================\n"
            f"{intro}"
            "\n================================================================\n"
            "Press any key to continue..."
            "\n================================================================\n"
        )
        timedKey(prompt=intro, resetOnInput=False, timeout=10)

    @classmethod
    def load_prompts(cls, preset_name: str) -> None | str:
        if cls.validate(preset_name):
            prompt_settings_file = (
                Path(__file__).parent / preset_name.replace(".", "/") / PROMPTS_FILE
            )
            if prompt_settings_file.exists():
                logger.typewriter_log(
                    f"Loading prompts from preset '{preset_name}'.", Fore.CYAN
                )
                return str(prompt_settings_file)
            else:
                logger.typewriter_log(
                    f"Preset '{preset_name}' does not have prompts.",
                    Fore.YELLOW,
                )
        return None
