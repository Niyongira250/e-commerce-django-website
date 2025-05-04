// profile.js

window.addEventListener('load', function() {
    const profileImg = document.querySelector('.profile-container img');
    if (profileImg) {
        profileImg.addEventListener('click', function() {
            this.classList.toggle('clicked');
        });
    }
});
