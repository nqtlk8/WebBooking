// API endpoints
const API_BASE_URL = 'http://localhost:8000';
const BOOKINGS_URL = `${API_BASE_URL}/bookings`;

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

// Check authentication on page load
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadBookingDetails();
});

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('userInfo');
    window.location.href = 'login.html';
}

// Load booking details
async function loadBookingDetails() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            window.location.href = 'booking.html';
            return;
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}`, {
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
            throw new Error('Failed to load booking details');
        }

        const booking = await response.json();

// Display booking details
        document.getElementById('bookingId').textContent = booking.id;
        document.getElementById('bookingStatus').textContent = booking.status;
        document.getElementById('bookingTime').textContent = new Date(booking.time).toLocaleString();
        
        // Calculate and display total amount
        let totalAmount = 0;
        const detailsContainer = document.getElementById('bookingDetails');
        detailsContainer.innerHTML = '';
        
        booking.booking_details.forEach(detail => {
            const subtotal = detail.ticket_type.price * detail.quantity;
            totalAmount += subtotal;

            const div = document.createElement('div');
            div.className = 'mb-2';
            div.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>${detail.ticket_type.name} x ${detail.quantity}</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
            `;
            detailsContainer.appendChild(div);
        });
        
        document.getElementById('totalAmount').textContent = `$${totalAmount.toFixed(2)}`;
        
    } catch (error) {
        console.error('Error loading booking details:', error);
        alert('Failed to load booking details');
    }
}

// Generate QR code
function generateQRCode() {
    const bookingId = localStorage.getItem('currentBookingId');
    if (!bookingId) {
        alert('No booking found');
        return;
    }

    // Create QR code content (booking ID + timestamp for uniqueness)
    const qrContent = `booking_${bookingId}_${Date.now()}`;
    
    // Generate QR code
    const qrCodeDiv = document.getElementById('qrCode');
    qrCodeDiv.innerHTML = ''; // Clear previous QR code
    
    new QRCode(qrCodeDiv, {
        text: qrContent,
        width: 200,
        height: 200,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });

    // Show QR code modal
    const qrModal = new bootstrap.Modal(document.getElementById('qrCodeModal'));
    qrModal.show();
}

// Confirm payment
async function confirmPayment() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            throw new Error('No booking found');
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}/confirm`, {
            method: 'POST',
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
            throw new Error('Failed to confirm payment');
        }

        // Close QR code modal
        bootstrap.Modal.getInstance(document.getElementById('qrCodeModal')).hide();

        // Show success message
        alert('Payment confirmed successfully!');
        
        // Redirect to booking page
        window.location.href = 'booking.html';

    } catch (error) {
        console.error('Error confirming payment:', error);
        alert(error.message || 'Failed to confirm payment');
    }
}

// Cancel booking
async function cancelBooking() {
    try {
        const bookingId = localStorage.getItem('currentBookingId');
        if (!bookingId) {
            throw new Error('No booking found');
        }

        if (!confirm('Are you sure you want to cancel this booking?')) {
            return;
        }

        const response = await fetch(`${BOOKINGS_URL}/${bookingId}/cancel`, {
            method: 'POST',
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
            throw new Error('Failed to cancel booking');
        }

        alert('Booking cancelled successfully');
        window.location.href = 'booking.html';

    } catch (error) {
        console.error('Error cancelling booking:', error);
        alert(error.message || 'Failed to cancel booking');
    }
} 