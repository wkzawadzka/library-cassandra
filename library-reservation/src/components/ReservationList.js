import * as React from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Paper from '@mui/material/Paper';
import { TableVirtuoso } from 'react-virtuoso';
import { TableRow, TableCell, IconButton, TableBody, Alert } from '@mui/material';
import TableHead from '@mui/material/TableHead';
import CheckIcon from '@mui/icons-material/Check';
import TableContainer from '@mui/material/TableContainer';
import Table from '@mui/material/Table';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';


function ReservationList() {
  const [reservations, setReservations] = useState([]);
  const [pagingState, setPagingState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [responseMessage, setResponseMessage] = useState('');
  const [responseType, setResponseType] = useState('');

  const navigate = useNavigate();

  useEffect(() => {
    fetchReservations();
  }, []);

  const fetchReservations = async (pagingState = null) => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/reservations', {
        params: {
          paging_state: pagingState,
        },
      });
      const formattedReservations = response.data.reservations.map((reservation) => ({
        ...reservation,
        reserved_at: new Date(reservation.reserved_at).toLocaleDateString('en-GB', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
        }),
      }));
      setReservations(formattedReservations);
      setPagingState(response.data.next_paging_state);
    } catch (error) {
      console.error('Failed to fetch reservations', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = async (bookId) => {
    try {
      await axios.delete(`http://localhost:8000/reservations/${bookId}`);
      setReservations(reservations.filter(reservation => reservation.book_id !== bookId));
      setResponseMessage('Reservation deleted successfully.');
      setResponseType('success');
    } catch (error) {
      console.error('There was an error deleting the reservation:', error);
      setResponseMessage('Failed to delete reservation.');
      setResponseType('error');
    }
  };

  const columns = [
    {
      width: 300,
      label: 'Reservation ID',
      dataKey: 'id',
    },
    {
      width: 300,
      label: 'User ID',
      dataKey: 'user_id',
    },
    {
      width: 300,
      label: 'Book ID',
      dataKey: 'book_id',
    },
    {
      width: 120,
      label: 'Reserved At',
      dataKey: 'reserved_at',
    },
  ];

  const fixedHeaderContent = () => {
    return (
      <TableHead>
        <TableRow>
          {columns.map((column) => (
            <TableCell
              key={column.dataKey}
              variant="head"
              align="left"
              style={{ width: column.width }}
            >
              {column.label}
            </TableCell>
          ))}
        </TableRow>
      </TableHead>
    );
  }

  const VirtuosoTableComponents = {
    Scroller: React.forwardRef((props, ref) => (
      <TableContainer component={Paper} {...props} ref={ref} />
    )),
    Table: (props) => (
      <Table {...props} sx={{ borderCollapse: 'separate', tableLayout: 'fixed' }} />
    ),
    TableHead,
    TableRow: ({ item: _item, ...props }) => <TableRow {...props} />,
    TableBody: React.forwardRef((props, ref) => <TableBody {...props} ref={ref} />),
  };

  const rowContent = (_index, row) => {
    return (
      <TableRow onClick={() => handleReservationClick(row.book_id)} style={{ cursor: 'pointer' }}>
        {columns.map((column) => (
          <TableCell key={column.dataKey} align="left" style={{ width: column.width }}>
            {row[column.dataKey]}
          </TableCell>
        ))}
        <TableCell align="right">
          <IconButton onClick={(event) => {
            event.stopPropagation();
            navigate(`/reservations/update/${row.book_id}/${row.user_id}`);
          }}>
            <EditIcon />
          </IconButton>
        </TableCell>
        <TableCell align="right">
          <IconButton onClick={(event) => {
            event.stopPropagation();
            handleDeleteClick(row.book_id);
          }}>
            <DeleteIcon />
          </IconButton>
        </TableCell>
      </TableRow>
    );
  };

  const handleReservationClick = (book_id) => {
    navigate(`/reservations/${book_id}`);
  };


  return (
    <>
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
    <Paper style={{ height: 400, width: '100%' }}>
      <TableVirtuoso
        data={reservations}
        components={VirtuosoTableComponents}
        fixedHeaderContent={fixedHeaderContent}
        itemContent={rowContent}
      />
    </Paper>
    </>
  );
};

export default ReservationList;