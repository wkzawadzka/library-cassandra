import React, { useState } from 'react';
import axios from 'axios';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import SendIcon from '@mui/icons-material/Send';
import Alert from '@mui/material/Alert';
import CheckIcon from '@mui/icons-material/Check';
import { useParams } from 'react-router-dom';

function ReservationUpdate() {
  const { book_id: old_book_id, user_id: old_user_id } = useParams();
  const [userId, setUserId] = useState(old_user_id);
  const [bookId, setBookId] = useState(old_book_id);
  const [responseMessage, setResponseMessage] = useState('');
  const [responseType, setResponseType] = useState('');

  const isUUID = (str) => {
    const regex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    return regex.test(str);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!isUUID(userId) || !isUUID(bookId)) {
      setResponseMessage('Both User ID and Book ID must be valid UUIDs.');
      setResponseType('error');
      return;
    }
    axios.put('http://localhost:8000/reservations/update/', {
      old_book_id: old_book_id,
      user_id: userId,
      book_id: bookId
    })
    .then(response => {
      setResponseMessage('Reservation updated successfully.');
      setResponseType('success');
    })
    .catch(error => {
      console.error('There was an error making the request:', error);

      if (error.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error response status:', error.response.status);
        console.error('Error response headers:', error.response.headers);

        if (error.response.data.detail) {
          setResponseMessage(error.response.data.detail);
        } else {
          setResponseMessage('Failed to create reservation');
        }
      } else if (error.request) {
        console.error('Error request:', error.request);
        setResponseMessage('No response received from the server.');
      } else {
        console.error('Error message:', error.message);
        setResponseMessage('Error in setting up the request: ' + error.message);
      }
      setResponseType('error');
    });
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        '& > :not(style)': { m: 1, width: '50ch' },
      }}
      noValidate
      autoComplete="off"
    >
      {responseMessage && (
        responseType === 'success' ? (
          <Alert icon={<CheckIcon fontSize="inherit" />} severity="success">
            {responseMessage}
          </Alert>
        ) : (
          <Alert severity="error">
            {responseMessage}
          </Alert>
        )
      )}
      <Typography variant="h5">Update Reservation</Typography>
      {/* <Typography variant="body1">Previous book_id: {old_book_id}</Typography>
      <Typography variant="body1">Previous user_id: {old_user_id}</Typography> */}
      <TextField
        id="user-id"
        label={`New User ID`}
        variant="outlined"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
      />
      <TextField
        id="book-id"
        label={`New Book ID`}
        variant="outlined"
        value={bookId}
        onChange={(e) => setBookId(e.target.value)}
      />
      <Button type="submit" variant="contained" size="large" endIcon={<SendIcon />}>Submit</Button>
    </Box>
  );
}

export default ReservationUpdate;