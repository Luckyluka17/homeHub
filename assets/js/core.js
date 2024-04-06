function restart() {
    fetch('/restart')
        .then(response => {
            if (response.ok) {
                const restartModal = new bootstrap.Modal('#restartStatus', {
                    keyboard: false
                });
                restartModal.show()
            }
    });
}