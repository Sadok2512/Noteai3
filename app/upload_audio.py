const backendUrl = "https://noteai3-production.up.railway.app";
const globalAudioPlayer = document.getElementById('globalAudioPlayer');
const audioPlayerContainer = document.querySelector('.audio-player-container');
const audioPlayerTrackTitle = document.getElementById('audioPlayerTrackTitle');
let currentlyPlayingNoteUrl = null;
let currentlyPlayingFilename = null;

function getFileInfo(filename) {
    const extension = filename.split('.').pop().toLowerCase();
    let typeDisplay = "DOCUMENT";
    let iconSrc = "./assets/icons/document-icon.svg";

    if (['pdf'].includes(extension)) {
        typeDisplay = "PDF";
        iconSrc = "./assets/icons/pdf-icon.svg";
    } else if (['doc', 'docx'].includes(extension)) {
        typeDisplay = "DOCX";
        iconSrc = "./assets/icons/doc-icon.svg";
    } else if (['ppt', 'pptx'].includes(extension)) {
        typeDisplay = "PPTX";
        iconSrc = "./assets/icons/ppt-icon.svg";
    } else if (['txt', 'rtf', 'csv'].includes(extension)) {
        typeDisplay = extension.toUpperCase();
        iconSrc = "./assets/icons/txt-icon.svg";
    } else if (['mp3', 'wav', 'ogg', 'm4a', 'webm'].includes(extension)) {
        typeDisplay = "AUDIO";
        iconSrc = "./assets/icons/audio-file-icon.svg";
    }
    return { typeDisplay, iconSrc };
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = Math.floor((now - date) / 86400000);
    const primary = diff === 0 ? "Aujourd’hui" : diff === 1 ? "Hier" : `${diff} jours`;
    const secondary = date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }).replace(':', 'h');
    return { primaryDate: primary, secondaryTime: secondary };
}

async function fetchHistory() {
    const userEmail = localStorage.getItem("userEmail");
    const token = localStorage.getItem("token");
    if (!userEmail || !token) return;

    const container = document.getElementById("historyTableBody");
    const emptyMessage = document.getElementById("emptyHistoryMessage");
    const paginationFooter = document.querySelector('.pagination-footer');
    const listContainer = document.querySelector('.file-list-container');

    emptyMessage.innerHTML = "<p>Chargement de vos notes...</p>";
    emptyMessage.style.display = "flex";
    container.innerHTML = "";
    paginationFooter.style.display = "none";
    listContainer.style.display = "none";

    try {
        const response = await fetch(`${backendUrl}/history/${userEmail}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        const data = await response.json();
        if (data.length === 0) {
            emptyMessage.innerHTML = "<p>Aucune note trouvée.</p>";
            listContainer.style.display = "block";
            return;
        }

        emptyMessage.style.display = "none";
        listContainer.style.display = "block";
        paginationFooter.style.display = "flex";

        data.forEach((note, index) => {
            const item = document.createElement("div");
            item.classList.add("history-item");
            item.setAttribute("role", "listitem");

            const sizeKB = note.size_bytes ? (note.size_bytes / 1024).toFixed(1) + " KB" : "N/A";
            const { primaryDate, secondaryTime } = formatDate(note.uploaded_at);
            const { typeDisplay, iconSrc } = getFileInfo(note.filename);
            const noteId = note.id || index;
            const storedAs = note.stored_as || note.filename;
            const encodedFilename = encodeURIComponent(note.filename);

            item.innerHTML = `
                <div class="col-checkbox"><input type="checkbox" id="cb-${noteId}"></div>
                <div class="col-name">
                    <div class="file-icon"><img src="${iconSrc}" alt="${typeDisplay}"></div>
                    <div class="file-info">
                        <p class="filename-text ${note.audio_url ? 'has-audio' : ''}" title="${note.filename}">${note.filename}</p>
                        <span class="file-type-subtitle">${typeDisplay}</span>
                    </div>
                </div>
                <div class="col-source mobile-hidden">${note.source || "WEB"}</div>
                <div class="col-size mobile-hidden">${sizeKB}</div>
                <div class="col-date mobile-hidden">
                    <span class="date-primary">${primaryDate}</span>
                    <span class="date-secondary">${secondaryTime}</span>
                </div>
                <div class="col-actions">
                    <a href="ainote.html?file=${storedAs}&filename=${encodedFilename}" class="action-icon-btn ainote-link" title="Ouvrir dans NoteAI">
                        <img src="./assets/icons/comment-icon.svg" alt="Ouvrir Note">
                    </a>
                </div>
            `;

            const fileNameEl = item.querySelector('.filename-text');
            if (note.audio_url && fileNameEl) {
                fileNameEl.addEventListener("click", (e) => {
                    e.stopPropagation();
                    if (globalAudioPlayer && audioPlayerContainer && audioPlayerTrackTitle) {
                        if (currentlyPlayingNoteUrl === note.audio_url && !globalAudioPlayer.paused) {
                            globalAudioPlayer.pause();
                        } else {
                            audioPlayerTrackTitle.textContent = note.filename;
                            globalAudioPlayer.src = note.audio_url;
                            globalAudioPlayer.play();
                            audioPlayerContainer.style.display = 'flex';
                            currentlyPlayingNoteUrl = note.audio_url;
                        }
                    }
                });
            }

            container.appendChild(item);
        });
    } catch (error) {
        console.error("HISTORY ERROR:", error);
        emptyMessage.innerHTML = "<p>Erreur lors du chargement. Veuillez réessayer.</p>";
        emptyMessage.style.display = "flex";
    }
}

window.addEventListener("DOMContentLoaded", fetchHistory);
