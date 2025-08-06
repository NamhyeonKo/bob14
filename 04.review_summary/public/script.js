async function submitReview() {
    const rating = document.querySelector('input[name="rating"]:checked');
    const opinion = document.getElementById('opinion').value;

    if (!rating || !opinion.trim()) {
        alert('평점 혹은 후기가 작성되지 않았습니다.');
        return;
    }

    const review = {
        rating: parseInt(rating.value),
        opinion
    };

    fetch('/api/reviews',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(review)
    })
}
   