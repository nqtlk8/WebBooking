// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const TICKET_TYPES_URL = `${API_BASE_URL}/ticket-types`;
const SEATS_URL = `${API_BASE_URL}/seats`;
const BOOKINGS_URL = `${API_BASE_URL}/bookings`;

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
        const name = document.getElementById('ticketTypeName').value.trim();
        const price = parseFloat(document.getElementById('ticketTypePrice').value);

        // Validate input
        if (!name) {
            alert('Please enter a ticket type name');
            return;
        }

        if (name.length > 100) {
            alert('Ticket type name must be less than 100 characters');
            return;
        }

        if (isNaN(price) || price <= 0) {
            alert('Please enter a valid price greater than 0');
            return;
        }

        // Round price to 2 decimal places
        const roundedPrice = Math.round(price * 100) / 100;

        const ticketType = {
            name: name,
            price: roundedPrice
        };

        const url = id ? `${TICKET_TYPES_URL}/${id}` : TICKET_TYPES_URL;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            ...defaultFetchOptions,
            method: method,
            body: JSON.stringify(ticketType)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || 'Failed to save ticket type';
            alert(errorMessage);
            return;
        }

        const savedTicketType = await response.json();
        
        // Show success message
        alert(id ? 'Ticket type updated successfully' : 'Ticket type created successfully');
        
        // Get the modal element
        const modalElement = document.getElementById('ticketTypeModal');
        const modal = bootstrap.Modal.getInstance(modalElement);
        
        // Remove focus from any focused element inside the modal
        if (document.activeElement && modalElement.contains(document.activeElement)) {
            document.activeElement.blur();
        }
        
        // Hide the modal
        modal.hide();
        
        // Reset form after modal is hidden
        document.getElementById('ticketTypeForm').reset();
        
        // Reload ticket types
        await loadTicketTypes();
    } catch (error) {
        console.error('Error saving ticket type:', error);
        alert('An error occurred while saving the ticket type');
    }
}

// Save seat
async function saveSeat() {
    try {
        if (!await checkAuth()) return;

        const id = document.getElementById('seatId').value;
        const ticketTypeId = document.getElementById('seatTicketType').value;
        const available = document.getElementById('seatStatus').value === 'true';
        const quantity = parseInt(document.getElementById('seatQuantity').value) || 1;

        if (id) {
            // If editing existing seat
            const seat = {
                ticket_type_id: parseInt(ticketTypeId),
                is_available: available
            };

            const url = `${SEATS_URL}/${id}`;
            const response = await fetch(url, {
                ...defaultFetchOptions,
                method: 'PUT',
                body: JSON.stringify(seat)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Error response:', errorData);
                handleAuthError(response);
                return;
            }
        } else {
            // If adding new seats using bulk creation
            const bulkSeat = {
                ticket_type_id: parseInt(ticketTypeId),
                is_available: available,
                quantity: quantity
            };

            const response = await fetch(`${SEATS_URL}/bulk`, {
                ...defaultFetchOptions,
                method: 'POST',
                body: JSON.stringify(bulkSeat)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error('Error response:', errorData);
                handleAuthError(response);
                return;
            }
        }

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
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || 'Failed to load ticket type';
            alert(errorMessage);
            return;
        }

        const ticketType = await response.json();

        // Fill the form with ticket type data
        document.getElementById('ticketTypeId').value = ticketType.id;
        document.getElementById('ticketTypeName').value = ticketType.name;
        document.getElementById('ticketTypePrice').value = ticketType.price;

        // Show the modal
        const modalElement = document.getElementById('ticketTypeModal');
        const modal = new bootstrap.Modal(modalElement);
        
        // Add event listener for when modal is shown
        modalElement.addEventListener('shown.bs.modal', function () {
            // Focus the first input when modal is shown
            document.getElementById('ticketTypeName').focus();
        });
        
        modal.show();
    } catch (error) {
        console.error('Error loading ticket type:', error);
        alert('An error occurred while loading the ticket type');
    }
}

// Delete ticket type
async function deleteTicketType(id) {
    try {
        if (!await checkAuth()) return;

        // Confirm deletion
        if (!confirm('Are you sure you want to delete this ticket type? This action cannot be undone.')) {
            return;
        }

        const response = await fetch(`${TICKET_TYPES_URL}/${id}`, {
            ...defaultFetchOptions,
            method: 'DELETE'
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || 'Failed to delete ticket type';
            alert(errorMessage);
            return;
        }

        // Reload ticket types after successful deletion
        await loadTicketTypes();
        alert('Ticket type deleted successfully');
    } catch (error) {
        console.error('Error deleting ticket type:', error);
        alert('An error occurred while deleting the ticket type');
    }
}

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadTicketTypes();
    loadBookings();
});

// Load bookings
async function loadBookings() {
    try {
        if (!await checkAuth()) return;

        const response = await fetch(`${BOOKINGS_URL}/admin/list`, {
            ...defaultFetchOptions
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        const bookings = await response.json();
        const tableBody = document.getElementById('bookingsTableBody');
        tableBody.innerHTML = '';

        bookings.forEach(booking => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${booking.id}</td>
                <td>${booking.user_name}</td>
                <td>$${booking.total_amount.toFixed(2)}</td>
                <td>
                    <span class="status-badge status-${booking.status.toLowerCase()}">
                        ${booking.status}
                    </span>
                </td>
                <td>
                    <button class="btn btn-sm btn-info me-2" onclick="viewBookingDetails(${booking.id})">
                        <i class="fas fa-eye"></i>
                    </button>
                    ${booking.status === 'PENDING' ? `
                        <button class="btn btn-sm btn-success me-2" onclick="updateBookingStatus(${booking.id}, 'CONFIRMED')">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="updateBookingStatus(${booking.id}, 'CANCELLED')">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        handleAuthError(error);
    }
}

// Update booking status
async function updateBookingStatus(bookingId, newStatus) {
    try {
        if (!await checkAuth()) return;

        const response = await fetch(`${BOOKINGS_URL}/admin/${bookingId}/status`, {
            ...defaultFetchOptions,
            method: 'PUT',
            body: JSON.stringify({ status: newStatus })
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        loadBookings(); // Reload the bookings list
    } catch (error) {
        handleAuthError(error);
    }
}

// View booking details
async function viewBookingDetails(bookingId) {
    try {
        if (!await checkAuth()) return;

        const response = await fetch(`${BOOKINGS_URL}/admin/${bookingId}`, {
            ...defaultFetchOptions
        });

        if (!response.ok) {
            handleAuthError(response);
            return;
        }

        const booking = await response.json();
        
        // Create modal content
        const modalContent = `
            <div class="modal-header">
                <h5 class="modal-title">Booking Details #${booking.id}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>User Name:</strong> ${booking.user_name}
                    </div>
                    <div class="col-md-6">
                        <strong>User Email:</strong> ${booking.user_email}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-6">
                        <strong>Status:</strong>
                        <span class="status-badge status-${booking.status.toLowerCase()}">
                            ${booking.status}
                        </span>
                    </div>
                    <div class="col-md-6">
                        <strong>Created At:</strong> ${new Date(booking.created_at).toLocaleString()}
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-12">
                        <strong>Total Amount:</strong> $${booking.total_amount.toFixed(2)}
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        `;

        // Create and show modal
        const modalDiv = document.createElement('div');
        modalDiv.className = 'modal fade';
        modalDiv.setAttribute('tabindex', '-1');
        modalDiv.setAttribute('role', 'dialog');
        modalDiv.setAttribute('aria-labelledby', 'bookingModalLabel');
        modalDiv.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    ${modalContent}
                </div>
            </div>
        `;
        document.body.appendChild(modalDiv);

        const modal = new bootstrap.Modal(modalDiv, {
            backdrop: 'static',
            keyboard: false
        });
        modal.show();

        // Remove modal from DOM after it's hidden
        modalDiv.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modalDiv);
        });
    } catch (error) {
        handleAuthError(error);
    }
}

// Add event listeners when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get the modal element
    const modalElement = document.getElementById('ticketTypeModal');
    
    // Add event listener for when modal is hidden
    modalElement.addEventListener('hidden.bs.modal', function () {
        // Remove focus from any focused element inside the modal
        if (document.activeElement && modalElement.contains(document.activeElement)) {
            document.activeElement.blur();
        }
    });
    
    // Add event listener for when modal is shown
    modalElement.addEventListener('shown.bs.modal', function () {
        // Focus the first input when modal is shown
        document.getElementById('ticketTypeName').focus();
    });
});
