
// PHẦN 1: CẤU HÌNH VÀ TRẠNG THÁI ỨNG DỤNG
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

const AppState = {
    cameras: [],
    violations: [],
    currentView: 'dashboard'
};

let editingCameraId = null;

const CONFIG = {
    districts: {
        'ba-dinh': 'Ba Đình', 'hoan-kiem': 'Hoàn Kiếm', 'dong-da': 'Đống Đa',
        'hai-ba-trung': 'Hai Bà Trưng', 'cau-giay': 'Cầu Giấy', 'thanh-xuan': 'Thanh Xuân',
        'hoang-mai': 'Hoàng Mai', 'long-bien': 'Long Biên'
    }
};

// PHẦN 2: LỚP TRUNG GIAN GỌI API (API HELPERS)
const api = {
    async getCameras() {
        const response = await fetch(`${API_BASE_URL}/cameras/`);
        if (!response.ok) throw new Error('Failed to fetch cameras');
        return await response.json();
    },
    async createCamera(cameraData) {
        const response = await fetch(`${API_BASE_URL}/cameras/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cameraData)
        });
        if (!response.ok) throw new Error('Failed to create camera');
        return await response.json();
    },
    async updateCamera(id, cameraData) {
        const response = await fetch(`${API_BASE_URL}/cameras/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(cameraData)
        });
        if (!response.ok) throw new Error('Failed to update camera');
        return await response.json();
    },
    async deleteCamera(id) {
        const response = await fetch(`${API_BASE_URL}/cameras/${id}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to delete camera');
        return await response.json();
    }
};

// PHẦN 3: CÁC HÀM TIỆN ÍCH VÀ HIỂN THỊ (RENDER)
const updateTime = () => {
    const timeElement = document.getElementById('current-time');
    if (timeElement) timeElement.textContent = new Date().toLocaleString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: '2-digit', year: 'numeric' });
};

const getYoutubeEmbedUrl = (url) => {
    try {
        const urlObj = new URL(url);
        let videoId = '';
        if (urlObj.hostname.includes('youtube.com')) {
            if (urlObj.pathname.startsWith('/live/')) {
                videoId = urlObj.pathname.split('/live/')[1];
            } else {
                videoId = urlObj.searchParams.get('v');
            }
        } else if (urlObj.hostname === 'youtu.be') {
            videoId = urlObj.pathname.slice(1);
        }
        if (videoId) {
            videoId = videoId.split('?')[0];
            return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&playlist=${videoId}&controls=0`;
        }
    } catch (e) { return null; }
    return null;
};

const renderApp = () => {
    renderCameraTable();
    renderVideoGrid();
    renderViolationsGrid();
    updateStats();
    updateDistrictFilters();
};

const renderCameraTable = () => {
    const tbody = document.getElementById('camera-table-body');
    if (AppState.cameras.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-12 text-center text-slate-400"><i class="fas fa-video-slash text-4xl mb-4"></i><p>Chưa có camera nào</p></td></tr>`;
        return;
    }
    tbody.innerHTML = AppState.cameras.map(camera => `
        <tr class="hover:bg-slate-800/30">
            <td class="px-6 py-4 text-sm text-slate-300">${camera.name}</td>
            <td class="px-6 py-4 text-sm text-slate-300">${CONFIG.districts[camera.district] || camera.district}</td>
            <td class="px-6 py-4 text-sm font-mono truncate max-w-xs">${camera.url}</td>
            <td class="px-6 py-4"><span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${camera.status === 'online' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}">${camera.status === 'online' ? 'Trực tuyến' : 'Ngoại tuyến'}</span></td>
            <td class="px-6 py-4"><div class="flex space-x-3"><button onclick="editCamera('${camera.id}')" class="text-blue-400 hover:text-blue-300" title="Chỉnh sửa"><i class="fas fa-edit"></i></button><button onclick="deleteCamera('${camera.id}')" class="text-red-400 hover:text-red-300" title="Xóa"><i class="fas fa-trash"></i></button></div></td>
        </tr>`).join('');
};

const renderVideoGrid = () => {
    const grid = document.getElementById('video-grid');
    if (AppState.cameras.length === 0) {
        grid.innerHTML = `<div class="col-span-full text-center text-slate-400 py-20"><i class="fas fa-video text-6xl mb-4"></i><p class="text-lg">Chưa có camera</p><p class="text-sm mt-2">Vui lòng vào "Quản lý Camera" để thêm mới</p></div>`;
        return;
    }
    grid.innerHTML = AppState.cameras.map(camera => {
        const embedUrl = getYoutubeEmbedUrl(camera.url);
        const placeholderContent = `<div class="video-placeholder flex flex-col items-center justify-center h-full text-slate-300/80"><i class="fas fa-video text-5xl mb-4 text-slate-500"></i><p class="font-semibold text-lg">Camera trực tiếp</p><p class="text-sm text-green-400/80">AI Monitoring Active</p></div>`;
        const videoContent = embedUrl ? `<iframe class="w-full h-full" src="${embedUrl}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>` : placeholderContent;
        return `<div class="grid-item bg-slate-800 rounded-2xl overflow-hidden shadow-lg border border-slate-700/50 flex flex-col"><div class="relative aspect-video bg-black">${videoContent}<div class="absolute top-3 left-3 bg-red-600/90 text-white text-xs font-bold px-2 py-1 rounded-md shadow-lg">LIVE</div><button onclick="showVideoModal('${camera.id}')" class="absolute bottom-3 left-3 w-8 h-8 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white transition-colors" title="Phóng to"><i class="fas fa-expand"></i></button></div><div class="px-2.5 py-2 flex items-center justify-between"><div><h3 class="font-bold text-lg leading-tight text-white truncate">${camera.name}</h3><p class="text-sm text-slate-400 flex items-center"><i class="fas fa-map-marker-alt mr-1.5 w-3"></i><span>${CONFIG.districts[camera.district] || camera.district}</span></p></div><div class="flex items-center space-x-2 text-green-400 text-sm font-medium"><div class="w-2 h-2 bg-green-400 rounded-full status-indicator"></div><span>Hoạt động</span></div></div></div>`;
    }).join('');
};

const renderViolationsGrid = () => {
    const grid = document.getElementById('violations-grid');
    if (AppState.violations.length === 0) {
        grid.innerHTML = `<div class="col-span-full text-center text-slate-400 py-20"><i class="fas fa-check-circle text-6xl mb-4"></i><p class="text-lg">Không có vi phạm nào</p></div>`;
    }
    // Logic hiển thị vi phạm sẽ được thêm ở đây
};

const updateStats = () => {
    document.getElementById('active-cameras').textContent = AppState.cameras.length;
    document.getElementById('camera-count').textContent = AppState.cameras.length;
    document.getElementById('total-violations').textContent = AppState.violations.length;
};

const updateDistrictFilters = () => {
    const districts = [...new Set(AppState.cameras.map(c => c.district))];
    ['district-filter', 'violation-district-filter'].forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            const val = select.value;
            select.innerHTML = '<option value="">Tất cả quận</option>' + districts.map(d => `<option value="${d}">${CONFIG.districts[d] || d}</option>`).join('');
            select.value = val;
        }
    });
};

const showNotification = (message, type = 'info') => {
    const notification = document.createElement('div');
    const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
    const colors = { success: 'bg-green-600', error: 'bg-red-600', info: 'bg-blue-600' };
    notification.className = `fixed top-5 right-5 z-50 px-6 py-4 rounded-xl shadow-lg text-white transition-transform duration-300 transform translate-x-[calc(100%+20px)] ${colors[type]}`;
    notification.innerHTML = `<div class="flex items-center space-x-3"><i class="fas ${icons[type]}"></i><span>${message}</span></div>`;
    document.body.appendChild(notification);
    setTimeout(() => notification.classList.remove('translate-x-[calc(100%+20px)]'), 100);
    setTimeout(() => {
        notification.classList.add('translate-x-[calc(100%+20px)]');
        notification.addEventListener('transitionend', () => notification.remove());
    }, 3000);
};

// PHẦN 4: CÁC HÀM XỬ LÝ SỰ KIỆN
window.showView = (viewName) => {
    document.querySelectorAll('.view-content').forEach(view => view.classList.add('hidden'));
    document.getElementById(`${viewName}-view`)?.classList.remove('hidden');
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`nav-${viewName}`)?.classList.add('active');
    AppState.currentView = viewName;
};

window.showAddCameraModal = () => {
    const modal = document.getElementById('add-camera-modal');
    modal.querySelector('h3').textContent = editingCameraId ? 'Chỉnh sửa Camera' : 'Thêm Camera Mới';
    modal.querySelector('button[type="submit"]').innerHTML = editingCameraId ? '<i class="fas fa-save mr-2"></i> Lưu thay đổi' : '<i class="fas fa-plus mr-2"></i> Thêm Camera';
    modal.classList.add('show');
};

window.hideAddCameraModal = () => {
    document.getElementById('add-camera-modal').classList.remove('show');
    document.getElementById('add-camera-form').reset();
    editingCameraId = null;
};

const handleGridSizeChange = (event) => {
    const gridElement = document.getElementById('video-grid');
    if (!gridElement) return;
    gridElement.classList.remove('grid-cols-2', 'grid-cols-3', 'grid-cols-4');
    const sizeMap = { '2x2': 'grid-cols-2', '4x4': 'grid-cols-4' };
    gridElement.classList.add(sizeMap[event.target.value] || 'grid-cols-3');
};

window.showVideoModal = (cameraId) => {
    const modal = document.getElementById('video-modal');
    const content = document.getElementById('video-modal-content');
    const camera = AppState.cameras.find(c => c.id === cameraId);
    if (!camera) return;
    const embedUrl = getYoutubeEmbedUrl(camera.url);
    content.innerHTML = embedUrl ? `<iframe class="w-full h-full" src="${embedUrl}" ...></iframe>` : `<div ...>Stream không hợp lệ</div>`;
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
};

window.hideVideoModal = () => {
    const modal = document.getElementById('video-modal');
    modal.classList.remove('show');
    modal.querySelector('#video-modal-content').innerHTML = '';
    document.body.style.overflow = 'auto';
};

const handleFormSubmit = async (event) => {
    event.preventDefault();
    const cameraData = {
        name: document.getElementById('camera-name').value,
        url: document.getElementById('camera-url').value,
        district: document.getElementById('camera-district').value,
        notes: document.getElementById('camera-notes').value,
        status: 'online'
    };

    try {
        if (editingCameraId) {
            const updatedCamera = await api.updateCamera(editingCameraId, cameraData);
            const index = AppState.cameras.findIndex(c => c.id === editingCameraId);
            if (index > -1) AppState.cameras[index] = updatedCamera;
            showNotification('Cập nhật camera thành công!', 'success');
        } else {
            const newCamera = await api.createCamera(cameraData);
            AppState.cameras.push(newCamera);
            showNotification('Thêm camera thành công!', 'success');
        }
        hideAddCameraModal();
        renderApp();
    } catch (error) {
        console.error("API Error:", error);
        showNotification(editingCameraId ? 'Cập nhật thất bại!' : 'Thêm camera thất bại!', 'error');
    }
};

window.editCamera = (cameraId) => {
    const camera = AppState.cameras.find(c => c.id === cameraId);
    if (!camera) return;
    editingCameraId = cameraId;
    document.getElementById('camera-name').value = camera.name;
    document.getElementById('camera-url').value = camera.url;
    document.getElementById('camera-district').value = camera.district;
    document.getElementById('camera-notes').value = camera.notes;
    showAddCameraModal();
};

window.deleteCamera = async (cameraId) => {
    if (!confirm('Bạn có chắc chắn muốn xóa camera này không?')) return;
    try {
        await api.deleteCamera(cameraId);
        AppState.cameras = AppState.cameras.filter(c => c.id !== cameraId);
        renderApp();
        showNotification('Đã xóa camera.', 'info');
    } catch (error) {
        console.error("API Error:", error);
        showNotification('Xóa thất bại!', 'error');
    }
};

// -------------------------------------------------------------------
// PHẦN 5: KHỞI TẠO ỨNG DỤNG
// -------------------------------------------------------------------
const initializeApp = async () => {
    document.getElementById('add-camera-form').addEventListener('submit', handleFormSubmit);
    document.getElementById('grid-size').addEventListener('change', handleGridSizeChange);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('video-modal').classList.contains('show')) {
            hideVideoModal();
        }
    });

    updateTime();
    setInterval(updateTime, 1000);

    try {
        showNotification('Đang tải dữ liệu từ server...', 'info');
        AppState.cameras = await api.getCameras();
        renderApp();
    } catch (error) {
        console.error("Initialization Error:", error);
        showNotification('Không thể tải dữ liệu từ server!', 'error');
    }
    console.log("Hệ thống giám sát đã sẵn sàng!");
};

document.addEventListener('DOMContentLoaded', initializeApp);