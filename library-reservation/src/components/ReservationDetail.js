import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import { CircularProgress, Box } from '@mui/material';

function ReservationDetail() {
  const { book_id } = useParams();
  const [reservation, setReservation] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/api/reservations/${book_id}`)
      .then(response => setReservation(response.data))
      .catch(error => console.error(error));
  }, [book_id]);

  if (!reservation) return (
    <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
      <CircularProgress />
    </Box>
  );

  return (
    <Card sx={{ maxWidth: 600, margin: 'auto', mt: 5 }}>
      {reservation.book.image_url && (
        <CardMedia
          component="img"
          height="300"
          image={reservation.book.image_url}
          alt={reservation.book.title}
        />
      )}
      <CardContent>
        <Typography variant="h5" component="div">
          Reservation Details
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Reservation ID: {reservation.id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          User ID: {reservation.user_id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Book ID: {reservation.book_id}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Reserved At: {new Date(reservation.reserved_at).toLocaleDateString()}
        </Typography>

        <Typography variant="h6" component="div" sx={{ mt: 2 }}>
          Book Details
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Title: {reservation.book.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Author: {reservation.book.author}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Category: {reservation.book.category}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default ReservationDetail;

