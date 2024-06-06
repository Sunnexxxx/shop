document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.sidebar .toggle');
    const modeSwitch = document.querySelector('.mode');
    const container = document.querySelector('.container');

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('close');
        container.classList.toggle('close');
    });

    modeSwitch.addEventListener('click', () => {
        document.body.classList.toggle('dark');
        const switchBtn = modeSwitch.querySelector('.toggle-switch');
        switchBtn.classList.toggle('active');
    });
});
