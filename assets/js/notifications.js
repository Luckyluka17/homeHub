function removeNotification(name) {
    fetch('/removeNotification?name='+name)
        .then(response => {
            if (response.ok) {
                alert('Notification supprimée.');
                window.location.href = "/";
            }
    });
}

function removeAllNotification() {
    fetch('/removeAllNotification')
        .then(response => {
            if (response.ok) {
                alert('Toutes les notifications ont étés supprimées.');
                window.location.href = "/";
            }
    });
}