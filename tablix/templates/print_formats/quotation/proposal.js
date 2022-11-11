jQuery.fn.toggleNext = function() {
  this.toggleClass('arrow-down')
    .next().slideToggle('fast');
};
$(document).ready(function() {
 $('#content #toc').each(function(index) {
    var $chapterTitle = $(this);
    var chapterId = 'chapter-' + (index + 1);
    $chapterTitle.attr('id', chapterId);
    $('#a'+index).attr('href','#' + chapterId);

 });
});

document.addEventListener('DOMContentLoaded', () => {
	const page_div = document.querySelector('.page-break');

	page_div.style.display = 'flex';
	page_div.style.flexDirection = 'column';

	const footer_html = document.getElementById('footer-html');
	footer_html.classList.add('hidden-pdf');
	footer_html.classList.remove('visible-pdf');
	footer_html.style.order = 1;
	footer_html.style.marginTop = '20px';
});

