document.addEventListener('DOMContentLoaded', function() {
  const feedbackDialog = document.getElementById('feedbackDialog');
  const thankYouDialog = document.getElementById('thankYouDialog');
  const feedbackForm = document.getElementById('feedbackForm');
  const cancelButton = document.getElementById('cancelButton');
  const closeThankYou = document.getElementById('closeThankYou');
  

  document.querySelector('#feedbackButton').addEventListener('click', () => {
    feedbackDialog.showModal()
  })

  document.querySelector('#feedbackButt').addEventListener('click', () => {
    feedbackDialog.showModal()
  })


  cancelButton.addEventListener('click', () => {
    if (feedbackDialog.open) {
      feedbackDialog.close()
    }
    
  });

  // kiitos ja moroo
  closeThankYou.addEventListener('click', () => {
    thankYouDialog.close();
  });

  // Palautteen lähetys backendille:
  feedbackForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
      firstName: document.getElementById('firstName').value,
      lastName: document.getElementById('lastName').value,
      nickname: document.getElementById('nickname').value,
      email: document.getElementById('email').value,
      feedback: document.getElementById('feedbackText').value,
    };


    try {
      const response = await fetch('http://localhost:5000/game/send/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      console.log(result);

      feedbackDialog.close();
      thankYouDialog.showModal();
      feedbackForm.reset();

    } catch (error) {
      console.error('Virhe palautteen lähetyksessä:', error);
    }
  });

  // Palautelaatikko sulkeutuu painaessasi mitä tahansa:
  feedbackDialog.addEventListener('click', (e) => {
    const dialogDimensions = feedbackDialog.getBoundingClientRect();
    if (
        e.clientX < dialogDimensions.left ||
        e.clientX > dialogDimensions.right ||
        e.clientY < dialogDimensions.top ||
        e.clientY > dialogDimensions.bottom
    ) {
      feedbackDialog.close();
    }
  });

  thankYouDialog.addEventListener('click', (e) => {
    const dialogDimensions = thankYouDialog.getBoundingClientRect();
    if (
        e.clientX < dialogDimensions.left ||
        e.clientX > dialogDimensions.right ||
        e.clientY < dialogDimensions.top ||
        e.clientY > dialogDimensions.bottom
    ) {
      thankYouDialog.close();
    }

closeThankYou.addEventListener('click', () => {
    window.parent.postMessage('closeFeedback', '*');
});
  });
});
