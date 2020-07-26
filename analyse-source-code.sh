#!/usr/bin/env bash

# specifies a set of variables to declare files to be used for code assessment
PACKAGE="speedtest"
CURRENT_DIR="."
PYCACHE_DIR="__pycache__"
PYPROJECT="pyproject.toml"

# specifies a set of variables to declare CLI output color
ERROR_OUT="\033[0;31m"
SUCCESS_OUT="\033[0;32m"
NONE_OUT="\033[0m"

# specifies code assessment notification signs
ALARM="🚨"
CAKE_TIME="✨ 🍰 ✨"


logging-box() {
:<<DOC
    Provides pretty-printer logging box
DOC
    tab="$*xxxx"
    format=${replace:--}
    echo -e "${tab//?/$format}"
    echo -e "$format $* $format"
    echo -e "${tab//?/$format}"
}


error-message() {
:<<DOC
    Prints error message
DOC
    echo -e "${ERROR_OUT}${1}${NONE_OUT} ${ALARM}" && exit 100
}


success-message() {
:<<DOC
    Prints success message
DOC
    echo -e "${SUCCESS_OUT}${1}${NONE_OUT} ${CAKE_TIME}"
}


remove-pycache() {
:<<DOC
    Removes python cache directories
DOC
    (
      find "${CURRENT_DIR}" -depth -name ${PYCACHE_DIR} | xargs rm -r
    ) || echo "No ${PYCACHE_DIR} dir found"
}


check-flake() {
:<<DOC
    Runs "flake8" static format checker assessment
DOC
    (
      logging-box "flake8 analysis" && flake8 "${CURRENT_DIR}"
    ) || error-message "flake8 analysis is failed"
}


check-mypy() {
:<<DOC
    Runs "mypy" static type checker assessment
DOC
    (
      logging-box "mypy analysis" && mypy "${CURRENT_DIR}"
    ) || error-message "mypy analysis is failed"
}


check-pymanifest() {
:<<DOC
    Runs analysis for package mandatory files using "check-manifest" tool
DOC
    (
      logging-box "check-manifest" && check-manifest -v "${CURRENT_DIR}"
    ) || error-message "manifest analysis is failed"
}


check-docstrings() {
:<<DOC
     Runs analysis for documentation code style formatter
DOC
    (
      logging-box "docstring analysis" &&
      interrogate --config "${PYPROJECT}" "${CURRENT_DIR}" &&
      logging-box "pydocstyle" &&
      pydocstyle --explain --count ${PACKAGE}
    ) || error-message "docstring analysis is failed"
}


check-black() {
:<<DOC
    Runs "black" code analyser
DOC
    (
      logging-box "black" && black --check ${PACKAGE}
    ) || error-message "black analysis is failed"
}


check-pylint() {
:<<DOC
    Runs "pylint" code analyser
DOC
   (
     logging-box "pylint" && find ${PACKAGE} -type f -name "*.py" | xargs pylint
   ) || error-message "pylint analysis is failed"
}


check-unittests() {
:<<DOC
    Runs unittests using "pytest" framework
DOC
   (
     logging-box "unit tests" && pytest
   ) || error-message "unit tests analysis is failed"
}


is-passed() {
:<<DOC
    Checks if code assessment is passed
DOC
    if [[ $? -ne 0 ]]; then
      error-message "Code assessment is failed, please fix errors"
    else
      success-message "Congratulations, code assessment is passed"
    fi
}


main() {
:<<DOC
    Runs "main" code analyser
DOC
    (
      remove-pycache
      check-black && \
      check-mypy && \
      check-pylint && \
      check-flake && \
      check-docstrings && \
      check-unittests && \
      is-passed
    )
}

main