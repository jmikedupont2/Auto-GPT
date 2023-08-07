from pathlib import Path

from colorama import Fore

from autogpt.logs import logger


class ProfileManager:
    _profiles = None

    @classmethod
    def get_all_profiles(cls):
        if cls._profiles is None:
            my_dir = Path(__file__).parent
            ai_files = my_dir.glob("**/ai_settings.json")
            prompt_files = my_dir.glob("**/prompt_settings.yaml")
            dirs = set(
                [file.parent.relative_to(my_dir) for file in ai_files]
                + [file.parent.relative_to(my_dir) for file in prompt_files]
            )
            cls._profiles = [".".join(dir.parts) for dir in dirs]
        return cls._profiles

    @classmethod
    def list_profiles(cls):
        # Find all files in this directory named "ai_settings.json"
        # Return a dot-separated list of the directory path relative to the turbo/profiles directory
        profiles = cls.get_all_profiles()
        count = len(profiles)

        logger.typewriter_log("\n")
        logger.typewriter_log(
            f"{count} PROFILE{'S' if count > 1 else ''} FOUND: ", Fore.CYAN
        )
        logger.typewriter_log("================================", Fore.CYAN)

        for i, profile in enumerate(profiles, 1):
            logger.typewriter_log(f"  [{i}] - {profile}", Fore.CYAN)

    @classmethod
    def validate_profile(cls, profile_name):
        if profile_name not in cls.get_all_profiles():
            logger.typewriter_log(
                f"Profile '{profile_name}' not found. Use '--ai-list' to see available profiles.",
                Fore.RED,
            )
            return False
        return True

    @classmethod
    def load_profile(cls, profile_name):
        if cls.validate_profile(profile_name):
            # Replace "." with "/" and add "ai_settings.yaml" to the end
            ai_settings_file = (
                Path(__file__).parent
                / profile_name.replace(".", "/")
                / "ai_settings.yaml"
            )
            
            if ai_settings_file.exists():
                ai_settings_file = str(ai_settings_file)
                logger.typewriter_log(
                    f"Loading ai settings profile for '{profile_name}'.", Fore.CYAN
                )
            else:
                ai_settings_file = None
                logger.typewriter_log(
                    f"Profile '{profile_name}' does not have ai settings.",
                    Fore.YELLOW,
                )

            prompt_settings_file = cls.load_profile_prompts(profile_name)
            return ai_settings_file, prompt_settings_file
        return None

    @classmethod
    def load_profile_prompts(cls, profile_name):
        if cls.validate_profile(profile_name):
            # Replace "." with "/" and add "ai_settings.yaml" to the end
            prompt_settings_file = (
                Path(__file__).parent
                / profile_name.replace(".", "/")
                / "prompt_settings.yaml"
            )
            if prompt_settings_file.exists():
                logger.typewriter_log(
                    f"Loading prompts from profile '{profile_name}'.", Fore.CYAN
                )
                return str(prompt_settings_file)
            else:
                logger.typewriter_log(
                    f"Profile '{profile_name}' does not have prompts.",
                    Fore.YELLOW,
                )
        return None
