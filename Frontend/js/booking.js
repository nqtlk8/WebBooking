// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const TICKET_TYPES_URL = `${API_BASE_URL}/ticket-types`;
const BOOKINGS_URL = `${API_BASE_URL}/bookings`;
const SEATS_URL = `${API_BASE_URL}/seats`;

// Kiểm tra xác thực
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const userInfo = JSON.parse(localStorage.getItem('userInfo'));
    
    if (!token || !userInfo || userInfo.type !== 'user') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('userInfo');
        window.location.href = 'login.html';
        return;
    }
    
    document.getElementById('userInfo').textContent = `Welcome, ${userInfo.name}`;
}

// State management
let selectedTickets = new Map(); // Map of ticket type ID to quantity
let currentBooking = null;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadTicketTypes();
});

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('userInfo');
    window.location.href = 'login.html';
}

// Load ticket types
async function loadTicketTypes() {
    try {
        const response = await fetch(TICKET_TYPES_URL, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            throw new Error('Failed to load ticket types');
        }

        const ticketTypes = await response.json();
        
        const container = document.getElementById('ticketTypesContainer');
        container.innerHTML = '';
        
        ticketTypes.forEach(ticketType => {
            const card = createTicketCard(ticketType);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading ticket types:', error);
        alert('Failed to load ticket types');
    }
}

// Create ticket card element
function createTicketCard(ticketType) {
    const col = document.createElement('div');
    col.className = 'col-md-6 mb-4';
    
    col.innerHTML = `
        <div class="card ticket-card h-100">
            <div class="card-body">
                <h5 class="card-title">${ticketType.name}</h5>
                <p class="card-text">Price: $${ticketType.price.toFixed(2)}</p>
                <div class="d-flex align-items-center">
                    <div class="input-group quantity-control">
                        <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(${ticketType.id}, -1)">-</button>
                        <input type="number" class="form-control text-center" id="quantity-${ticketType.id}" value="0" min="0" readonly>
                        <button class="btn btn-outline-secondary" type="button" onclick="updateQuantity(${ticketType.id}, 1)">+</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

// Update ticket quantity
function updateQuantity(ticketTypeId, change) {
    const input = document.getElementById(`quantity-${ticketTypeId}`);
    const currentValue = parseInt(input.value) || 0;
    const newValue = Math.max(0, currentValue + change);
    
    input.value = newValue;
    
    if (newValue > 0) {
        selectedTickets.set(ticketTypeId, newValue);
    } else {
        selectedTickets.delete(ticketTypeId);
    }
    
    updateSelectionSummary();
}

// Update selection summary
function updateSelectionSummary() {
    const container = document.getElementById('selectedTickets');
    const proceedButton = document.getElementById('proceedButton');
    let total = 0;
    
    container.innerHTML = '';
    
    if (selectedTickets.size === 0) {
        container.innerHTML = '<p class="text-muted">No tickets selected</p>';
        proceedButton.disabled = true;
        document.getElementById('totalAmount').textContent = '$0.00';
        return;
    }
    
    selectedTickets.forEach((quantity, ticketTypeId) => {
        const ticketType = getTicketTypeById(ticketTypeId);
        if (ticketType) {
            const subtotal = ticketType.price * quantity;
            total += subtotal;
            
            const div = document.createElement('div');
            div.className = 'mb-2';
            div.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>${ticketType.name} x ${quantity}</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
            `;
            container.appendChild(div);
        }
    });
    
    document.getElementById('totalAmount').textContent = `$${total.toFixed(2)}`;
    proceedButton.disabled = false;
}

// Get ticket type by ID
function getTicketTypeById(id) {
    const cards = document.querySelectorAll('.ticket-card');
    for (const card of cards) {
        const title = card.querySelector('.card-title').textContent;
        const price = parseFloat(card.querySelector('.card-text').textContent.replace('Price: $', ''));
        if (card.querySelector(`#quantity-${id}`)) {
            return { id, name: title, price };
        }
    }
    return null;
}

// Proceed to payment
async function proceedToPayment() {
    try {
        const token = localStorage.getItem('access_token');
        console.log('Token from localStorage:', token);
        
        if (!token) {
            throw new Error('No authentication token found. Please log in again.');
        }

        // Create booking
        const userInfo = JSON.parse(localStorage.getItem('userInfo'));
        console.log('User info from localStorage:', userInfo);
        
        if (!userInfo || !userInfo.id) {
            throw new Error('User information not found. Please log in again.');
        }

        const seatsRequested = Array.from(selectedTickets.entries()).map(([ticket_type_id, quantity]) => ({
            ticket_type_id,
            quantity
        }));
        
        if (seatsRequested.length === 0) {
            throw new Error('Please select at least one ticket before proceeding.');
        }

        const requestData = {
            user_id: userInfo.id,
            seats_requested: seatsRequested
        };

        console.log('Making request to:', `${BOOKINGS_URL}/initiate`);
        console.log('Request data:', requestData);

        const response = await fetch(`${BOOKINGS_URL}/initiate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }
            const errorData = await response.json();
            console.error('Error response:', errorData);
            throw new Error(errorData.detail || 'Failed to create booking');
        }
        
        const bookingData = await response.json();
        console.log('Booking response:', bookingData);
        
        // Store booking ID in localStorage and redirect to payment page
        localStorage.setItem('currentBookingId', bookingData.id);
        window.location.href = 'payment.html';

    } catch (error) {
        console.error('Error creating booking:', error);
        alert(error.message || 'Failed to create booking');
    }
}
