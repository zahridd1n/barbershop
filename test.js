fetch('https://bossbarber.uz/api/api28/headers/')
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('Network response was not ok');
    }
  })
  .then(data => {
    console.log('Data fetched successfully:', data);
  })
  .catch(error => {
    if (error.message.includes('Failed to fetch')) {
      console.error('CORS error or network issue:', error);
    } else {
      console.error('Error:', error);
    }
  });
