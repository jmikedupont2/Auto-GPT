from pathlib import Path

from colorama import Fore
from pytimedinput import timedInput, timedKey

from autogpt.logs import logger

SETTINGS_FILE = "ai.yaml"
PROMPTS_FILE = "prompts.yaml"
PERSONA_CONFIG_DIR = Path(__file__).parent.parent.parent / "config" / "personas"
TIMEOUT_SECONDS = 5


class PersonaManager:
    _personas = None

    @classmethod
    def get_all(cls) -> list[str]:
        if cls._personas is None:
            ai_files = PERSONA_CONFIG_DIR.glob(f"**/{SETTINGS_FILE}")
            prompt_files = PERSONA_CONFIG_DIR.glob(f"**/{PROMPTS_FILE}")
            dirs = set(
                [file.parent.relative_to(PERSONA_CONFIG_DIR) for file in ai_files]
                + [file.parent.relative_to(PERSONA_CONFIG_DIR) for file in prompt_files]
            )
            cls._personas = [".".join(dir.parts) for dir in dirs]
            cls._personas.sort()
        return cls._personas

    @classmethod
    def list(cls) -> None:
        personas = cls.get_all()
        count = len(personas)

        logger.typewriter_log("\n")
        logger.typewriter_log(
            f"{count} PERSONAS{'S' if count > 1 else ''} FOUND: ", Fore.CYAN
        )
        logger.typewriter_log("================================", Fore.CYAN)

        for i, persona in enumerate(personas, 1):
            logger.typewriter_log(f"  [{i}] - {persona}", Fore.CYAN)

    @classmethod
    def prompt_user(cls, config) -> None:
        cls.list()
        logger.typewriter_log("\n")

        persona, _ = timedInput(
            prompt=f"{Fore.CYAN}Choose number or name. Enter or wait {TIMEOUT_SECONDS}s to skip: ",
            resetOnInput=True,
            timeout=TIMEOUT_SECONDS,
        )

        if persona:
            try:
                persona_int = int(persona)
                if persona_int > 0 and persona_int <= len(cls.get_all()):
                    persona_name = cls.get_all()[persona_int - 1]
                    return cls.load(persona_name)
            except ValueError:
                if cls.validate(persona):
                    return cls.load(persona)

            logger.typewriter_log(
                f"'{persona}' persona not found. Skiping...",
                Fore.RED,
            )
        return None, None

    @classmethod
    def validate(cls, persona_name: str) -> bool:
        return persona_name in cls.get_all()

    @classmethod
    def load(cls, persona_name: str) -> tuple[str | None, str | None]:
        if cls.validate(persona_name):
            logger.typewriter_log(f"Loading '{persona_name}' persona.", Fore.CYAN)
            ai_settings_file = (
                PERSONA_CONFIG_DIR / persona_name.replace(".", "/") / SETTINGS_FILE
            )

            if ai_settings_file.exists():
                ai_settings = str(ai_settings_file)
                logger.typewriter_log(
                    f"Loading '{persona_name}' ai settings.", Fore.CYAN
                )
            else:
                ai_settings = None
                logger.typewriter_log(
                    f"'{persona_name}' has no ai settings. You will need to provide them manually.",
                    Fore.YELLOW,
                )

            prompt_settings = cls.load_prompts(persona_name)
            cls.display_intro(persona_name)
            return ai_settings, prompt_settings
        return None, None

    @classmethod
    def display_intro(cls, persona_name: str) -> None | str:
        intro_file = PERSONA_CONFIG_DIR / persona_name.replace(".", "/") / "intro.md"

        if not intro_file.exists():
            return None

        intro = intro_file.read_text()

        intro = (
            f"{Fore.CYAN}"
            "\n================================================================\n"
            f"{intro}"
            "\n================================================================\n"
            f"Press any key or wait {TIMEOUT_SECONDS}s to continue..."
            "\n================================================================\n"
        )
        timedKey(prompt=intro, resetOnInput=False, timeout=TIMEOUT_SECONDS)

    @classmethod
    def load_prompts(cls, persona_name: str) -> None | str:
        if cls.validate(persona_name):
            prompt_settings_file = (
                PERSONA_CONFIG_DIR / persona_name.replace(".", "/") / PROMPTS_FILE
            )
            if prompt_settings_file.exists():
                logger.typewriter_log(f"Loading '{persona_name} prompts'.", Fore.CYAN)
                return str(prompt_settings_file)
            else:
                logger.typewriter_log(
                    f"'{persona_name}' has no prompts. Using default...",
                    Fore.YELLOW,
                )
        return None
