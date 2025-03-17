document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('dealForm');

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const address = document.getElementById('address').value;

    const dealData = {
      seller_name: "Website Lead",
      property_address: address,
      deal_type: "Analyzer Only",
      notes: "Submitted via homepage analyzer form."
    };

    fetch('/submit-deal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(dealData)
    })
    .then(response => response.json())
    .then(data => {
      const resultDiv = document.getElementById('results');
      resultDiv.innerHTML = `
        <h3>✅ Deal Submitted!</h3>
        <p><strong>AI Summary:</strong><br>${data.ai_summary}</p>
      `;
    })
    .catch(err => {
      console.error(err);
      document.getElementById('results').innerHTML = '<p>❌ There was a problem submitting the deal.</p>';
    });
});
});
