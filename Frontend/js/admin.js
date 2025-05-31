// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const TICKET_TYPES_URL = `${API_BASE_URL}/ticket-types`;
const SEATS_URL = `${API_BASE_URL}/seats`;

// Kiểm tra xác thực
async function checkAuth() {
    const token = localStorage.getItem('access_token');
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    
    if (!token || !userInfo || userInfo.type !== 'admin') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        window.location.href = '../html/adminlogin.html';
        return false;
    }
    return true;
}

// Default fetch options
const defaultFetchOptions = {
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    }
};

console.log('Admin JS loaded');

// Xử lý lỗi xác thực
function handleAuthError(error) {
    console.error('Authentication error:', error);
    if (error.message === 'Unauthorized' || error.status === 401) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        window.location.href = '../html/adminlogin.html';
    } else {
        throw error;
    }
}

// Load all ticket types
async function loadTicketTypes() {
    try {
        if (!await checkAuth()) return;
        // Lấy danh sách loại vé
        const response = await fetch(TICKET_TYPES_URL, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        const ticketTypes = await response.json();

        // Lấy thông tin số lượng ghế theo loại vé
        const countResponse = await fetch(`${API_BASE_URL}/seats/count`, {
            ...defaultFetchOptions,
            method: 'GET'
        });

        if (!countResponse.ok) {
            handleAuthError(countResponse);
            return;
        }

        const seatCounts = await countResponse.json();
        const ticketTypeSeatCounts = seatCounts.ticket_type_counts;

        // Cập nhật tổng quan
        document.getElementById('totalSeats').textContent = seatCounts.total_seats;
        document.getElementById('availableSeats').textContent = seatCounts.available_seats;
        document.getElementById('bookedSeats').textContent = seatCounts.not_available_seats;

        const tableBody = document.getElementById('ticketTypesTableBody');
        const selectElement = document.getElementById('seatTicketType');

        // Xóa dữ liệu cũ
        tableBody.innerHTML = '';
        selectElement.innerHTML = '';

        // Duyệt từng loại vé
        ticketTypes.forEach(type => {
            const count = ticketTypeSeatCounts.find(c => c.ticket_type_id === type.id) || {
                total_seats: 0,
                available_seats: 0,
                not_available_seats: 0
            };

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${type.id}</td>
                <td>${type.name}</td>
                <td>$${type.price.toFixed(2)}</td>
                <td>${count.total_seats}</td>
                <td>${count.available_seats}</td>
                <td>${count.not_available_seats}</td>
                <td>
                    <button class="btn btn-sm btn-warning" onclick="editTicketType(${type.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteTicketType(${type.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tableBody.appendChild(row);

            // Thêm vào dropdown chọn loại vé
            const option = document.createElement('option');
            option.value = type.id;
            option.textContent = type.name;
            selectElement.appendChild(option);
        });
    } catch (error) {
        handleAuthError(error);
    }
}

// Save ticket type
async function saveTicketType() {
    try {
        if (!await checkAuth()) return;

        const id = document.getElementById('ticketTypeId').value;
        const name = document.getElementById('ticketTypeName').value;
        const price = document.getElementById('ticketTypePrice').value;

        const ticketType = {
            name: name,
            price: parseFloat(price)
        };

        const url = id ? `${TICKET_TYPES_URL}/${id}` : TICKET_TYPES_URL;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            ...defaultFetchOptions,
            method: method,
            body: JSON.stringify(ticketType)
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        bootstrap.Modal.getInstance(document.getElementById('ticketTypeModal')).hide();
        loadTicketTypes();
        document.getElementById('ticketTypeForm').reset();
    } catch (error) {
        handleAuthError(error);
    }
}

// Save seat
async function saveSeat() {
    try {
        if (!await checkAuth()) return;

        const id = document.getElementById('seatId').value;
        const ticketTypeId = document.getElementById('seatTicketType').value;
        const available = document.getElementById('seatStatus').value === 'true';

        const seat = {
            ticket_type_id: parseInt(ticketTypeId),
            is_available: available
        };

        const url = id ? `${SEATS_URL}/${id}` : SEATS_URL;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            ...defaultFetchOptions,
            method: method,
            body: JSON.stringify(seat)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            console.error('Error response:', errorData);
            handleAuthError(response);
            return;
        }

        const result = await response.json();
        console.log('Success:', result);

        bootstrap.Modal.getInstance(document.getElementById('seatModal')).hide();
        loadTicketTypes();
        document.getElementById('seatForm').reset();
    } catch (error) {
        console.error('Error in saveSeat:', error);
        handleAuthError(error);
    }
}

// Edit ticket type
async function editTicketType(id) {
    try {
        if (!await checkAuth()) return;

        const response = await fetch(`${TICKET_TYPES_URL}/${id}`, {
            ...defaultFetchOptions,
            method: 'GET'
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        const ticketType = await response.json();

        document.getElementById('ticketTypeId').value = ticketType.id;
        document.getElementById('ticketTypeName').value = ticketType.name;
        document.getElementById('ticketTypePrice').value = ticketType.price;

        const modal = new bootstrap.Modal(document.getElementById('ticketTypeModal'));
        modal.show();
    } catch (error) {
        handleAuthError(error);
    }
}

// Delete ticket type
async function deleteTicketType(id) {
    try {
        if (!await checkAuth()) return;

        if (!confirm('Are you sure you want to delete this ticket type?')) {
            return;
        }

        const response = await fetch(`${TICKET_TYPES_URL}/${id}`, {
            ...defaultFetchOptions,
            method: 'DELETE'
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        loadTicketTypes();
    } catch (error) {
        handleAuthError(error);
    }
}

// Khởi tạo khi trang được load
document.addEventListener('DOMContentLoaded', async function() {
    if (!await checkAuth()) return;
    loadTicketTypes();
});
