from pathlib import Path

from colorama import Fore

from autogpt.logs import logger

SETTINGS_FILE = "ai.yaml"
PROMPTS_FILE = "prompts.yaml"


class PersonaManager:
    _personas = None

    @classmethod
    def get_all(cls) -> list[str]:
        if cls._personas is None:
            my_dir = Path(__file__).parent
            ai_files = my_dir.glob(f"**/{SETTINGS_FILE}")
            prompt_files = my_dir.glob(f"**/{PROMPTS_FILE}")
            dirs = set(
                [file.parent.relative_to(my_dir) for file in ai_files]
                + [file.parent.relative_to(my_dir) for file in prompt_files]
            )
            cls._personas = [".".join(dir.parts) for dir in dirs]
        return cls._personas

    @classmethod
    def list(cls) -> None:
        personas = cls.get_all()
        count = len(personas)

        logger.typewriter_log("\n")
        logger.typewriter_log(
            f"{count} PERSONA{'S' if count > 1 else ''} FOUND: ", Fore.CYAN
        )
        logger.typewriter_log("================================", Fore.CYAN)

        for i, persona in enumerate(personas, 1):
            logger.typewriter_log(f"  [{i}] - {persona}", Fore.CYAN)

    @classmethod
    def validate(cls, persona_name: str) -> bool:
        if persona_name not in cls.get_all():
            logger.typewriter_log(
                f"Profile '{persona_name}' not found. Use '--personas' to see available personas.",
                Fore.RED,
            )
            return False
        return True

    @classmethod
    def load(cls, persona_name: str) -> tuple[str | None, str | None]:
        if cls.validate(persona_name):
            ai_settings_file = (
                Path(__file__).parent / persona_name.replace(".", "/") / SETTINGS_FILE
            )

            if ai_settings_file.exists():
                ai_settings = str(ai_settings_file)
                logger.typewriter_log(
                    f"Loading ai settings persona for '{persona_name}'.", Fore.CYAN
                )
            else:
                ai_settings = None
                logger.typewriter_log(
                    f"Persona '{persona_name}' does not have ai settings.",
                    Fore.YELLOW,
                )

            prompt_settings = cls.load_prompts(persona_name)
            return ai_settings, prompt_settings
        return None, None

    @classmethod
    def load_prompts(cls, persona_name: str) -> None | str:
        if cls.validate(persona_name):
            prompt_settings_file = (
                Path(__file__).parent / persona_name.replace(".", "/") / PROMPTS_FILE
            )
            if prompt_settings_file.exists():
                logger.typewriter_log(
                    f"Loading prompts from persona '{persona_name}'.", Fore.CYAN
                )
                return str(prompt_settings_file)
            else:
                logger.typewriter_log(
                    f"Persona '{persona_name}' does not have prompts.",
                    Fore.YELLOW,
                )
        return None
