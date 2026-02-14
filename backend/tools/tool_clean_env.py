from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import shutil
from datetime import datetime
from typing import Any, Dict

from config import get_settings
from logger import logger


def resolve_path() -> Dict[str, Path]:
    # base_dir
    logger.debug("resolve_path called")
    base_dir = Path(__file__).resolve().parent.parent
    logger.debug(f"base_dir: {base_dir}")

    # output_path
    settings = get_settings()
    output_dir = settings.output_dir
    output_path = base_dir / output_dir

    # app_path
    app_path = output_path / "app"

    # tests_path
    tests_path = output_path / "tests"

    # public_path
    public_path = output_path / "public"

    # results_path
    results_dir = settings.test_results_dir
    results_path = base_dir / output_dir / results_dir

    # prepare_path
    prepare_path = output_path / "prepare"

    # sample_path
    sample_path = base_dir / "sample"

    # backup_path
    backup_path = base_dir / "backup"

    paths = {
        "output_path": output_path,
        "app_path": app_path,
        "tests_path": tests_path,
        "public_path": public_path,
        "results_path": results_path,
        "prepare_path": prepare_path,
        "sample_path": sample_path,
        "backup_path": backup_path,
    }
    logger.debug(f"paths: {paths}")
    return paths


def precheck_required_files(paths: Dict[str, Any]) -> None:
    logger.debug("precheck_required_files called")

    # --- check directories ---
    # (a) check output/app
    app_path = paths["app_path"]
    if not app_path.is_dir():
        raise RuntimeError(f"{app_path} not found.")

    # (b) check output/tests
    tests_path = paths["tests_path"]
    if not tests_path.is_dir():
        raise RuntimeError(f"{tests_path} not found.")

    # (c) check output/public
    public_path = paths["public_path"]
    if not public_path.is_dir():
        raise RuntimeError(f"{public_path} not found.")

    # (d) check output/results
    results_path = paths["results_path"]
    if not results_path.is_dir():
        raise RuntimeError(f"{results_path} not found.")

    # (e) check backup directory
    backup_path: Path = paths["backup_path"]
    backup_path.mkdir(exist_ok=True)

    # --- check files ---
    # (a) check output/prepare/hotel.png
    prepare_hotel_file = paths["prepare_path"] / "hotel.png"
    if not prepare_hotel_file.is_file():
        raise RuntimeError(f"{prepare_hotel_file} not found.")

    # (b) check output/tests/base.spec.ts
    base_spec_file = paths["tests_path"] / "base.spec.ts"
    if not base_spec_file.is_file():
        raise RuntimeError(f"{base_spec_file} not found.")


def backup_targets(paths: Dict[str, Path]) -> None:
    logger.info("== Backup targets ==")
    backup_root = paths["backup_path"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / timestamp
    logger.info(f"Backup directory: {backup_dir}")

    for key in ["app_path", "tests_path", "results_path"]:
        src = paths[key]
        dst = backup_dir / src.name
        logger.log("TOOL", f"Backup Copy: {src} -> {dst}")
        shutil.copytree(src, dst, copy_function=shutil.copy2)


def restore_app_page(paths: Dict[str, Path]) -> None:
    logger.info("== Restore original app/page.tsx ==")

    # copy sample/app/page_org.tsx -> output/app/page.tsx
    sample_path = paths["sample_path"]
    sample_page = sample_path / "app" / "page_org.tsx"
    logger.debug(f"Sample page: {sample_page}")
    if not sample_page.is_file():
        raise RuntimeError(f"{sample_page} not found.")

    app_path = paths["app_path"]
    app_page = app_path / "page.tsx"
    logger.log("TOOL", f"Initial page.tsx Copy: {sample_page} -> {app_page}")
    shutil.copy2(sample_page, app_page)

    # copy sample/app/layout_indicator.tsx -> output/app/layout.tsx
    sample_layout = sample_path / "app" / "layout_indicator.tsx"
    logger.debug(f"Sample layout: {sample_layout}")
    if not sample_layout.is_file():
        raise RuntimeError(f"{sample_layout} not found.")

    app_layout = app_path / "layout.tsx"
    logger.log("TOOL", f"Initial layout.tsx Copy: {sample_layout} -> {app_layout}")
    shutil.copy2(sample_layout, app_layout)


def clean_dot_next(paths: Dict[str, Path]) -> None:
    logger.info("== Clean Next.js cache (.next) ==")

    output_path = paths["output_path"]
    dot_next_dir = output_path / ".next"

    if not dot_next_dir.is_dir():
        logger.warning(f"[CLEAN_DOT_NEXT] .next dir not found. skip: {dot_next_dir}")
        return
    logger.log(
        "TOOL",
        f"[CLEAN_DOT_NEXT] Remove Next.js cache directory recursively: {dot_next_dir}",
    )
    shutil.rmtree(dot_next_dir)


def clean_app_booking(paths: Dict[str, Path]) -> None:
    logger.info("== Clean output/app/booking/* ==")
    booking_dir = paths["app_path"] / "booking"
    if not booking_dir.is_dir():
        logger.warning(
            f"[CLEAN_APP_BOOKING] booking dir not found. skip: {booking_dir}"
        )
        return
    logger.log(
        "TOOL", f"[CLEAN_APP_BOOKING] Remove directory recursively: {booking_dir}"
    )
    shutil.rmtree(booking_dir)


def clean_components(paths: Dict[str, Path]) -> None:
    logger.info("== Clean output/app/components ==")
    compo_path = paths["app_path"] / "components"
    if not compo_path.is_dir():
        logger.warning(
            f"[CLEAN_COMPONETS] components dir not found. skip: {compo_path}"
        )
        return

    logger.log("TOOL", f"[CLEAN_COMPONENTS] Remove directory recursively: {compo_path}")
    shutil.rmtree(compo_path)


def clean_public_hotel(paths: Dict[str, Path]) -> None:
    logger.info("== Clean output/public/hotel.png ==")
    public_path = paths["public_path"]
    hotel_path = public_path / "hotel.png"
    if not hotel_path.exists():
        logger.warning(f"[CLEAN_PUBLIC_HOTEL] hotel.png not found. skip: {hotel_path}")
        return
    logger.log("TOOL", f"[CLEAN_PUBLIC_HOTEL] Remove: {hotel_path}")
    hotel_path.unlink()


def clean_tests(paths: Dict[str, Path]) -> None:
    logger.info("== Clean output/tests/*.spec.ts ==")
    tests_dir = paths["tests_path"]

    spec_files = list(tests_dir.glob("*.spec.ts"))
    if not spec_files:
        logger.warning(f"[CLEAN_TESTS] no *.spec.ts files found in {spec_files}.")
        return

    for spec in spec_files:
        if spec.name == "base.spec.ts":
            logger.warning(f"[CLEAN TESTS] Keep 'base.spec.ts': {spec.name}")
            continue
        else:
            logger.log("TOOL", f"[CLEAN_TESTS] Remove: {spec}")
            spec.unlink()
    return


def clean_results(paths: Dict[str, Path]) -> None:
    logger.info("== Clean output/results/*.json, screenshot ==")
    results_dir = paths["results_path"]

    # remove output/results/*.json
    json_files = list(results_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"[CLEAN_RESULTS] no *.json files found in {results_dir}")
    else:
        for json_file in json_files:
            logger.debug(f"[CLEAN_RESULTS] Remove: {json_file}")
            json_file.unlink()

    # remove output/results/screenshot/*.png
    screenshot_dir = paths["results_path"] / "screenshot"
    if not screenshot_dir.is_dir():
        logger.warning(f"[CLEAN_RESULTS] screenshot dir not found in {results_dir}")
        return
    else:
        logger.log(
            "TOOL", f"[CLEAN_RESULTS] Remove directory recursively: {screenshot_dir}"
        )
        shutil.rmtree(screenshot_dir)


def main() -> int:
    logger.info("Cleaning output and setup start")
    paths = resolve_path()

    try:
        # precheck
        error_message = "precheck_required_files"
        precheck_required_files(paths=paths)

        # backup
        error_message = "backup_targets"
        backup_targets(paths=paths)

        # restore page
        error_message = "restore_app_page"
        restore_app_page(paths=paths)

        # clean .next
        error_message = "clean_dot_next"
        clean_dot_next(paths=paths)

        # clean output/app/booking/*
        error_message = "clean_app_booking"
        clean_app_booking(paths=paths)

        # clean output/app/components/*.tsx
        error_message = "clean_components"
        clean_components(paths=paths)

        # clean output/public/hotel.png
        error_message = "clean_public_hotel"
        clean_public_hotel(paths=paths)

        # clean output/tests/*.spec.ts
        error_message = "clean_tests"
        clean_tests(paths=paths)

        # clean output/results/*.json, output/results/screenshot/*.png
        error_message = "clean_results"
        clean_results(paths=paths)

    except Exception as e:
        logger.error(f"{error_message}: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
