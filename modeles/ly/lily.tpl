#(set-global-staff-size <<<!proprietes['portee_taille']>>>)

allowGrobCallback =
#(define-scheme-function (parser location syms) (symbol-list?)
   (let ((interface (car syms))
         (sym (cadr syms)))
     #{
       \with {
         \consists #(lambda (context)
                      `((acknowledgers .
                          ((,interface . ,(lambda (engraver grob source-engraver)
                                            (let ((prop (ly:grob-property grob sym)))
                                              (if (procedure? prop) (ly:grob-set-property! grob sym (prop grob)))
                                              ))))
                          ))
                      )
       }
     #}))

absFontSize =
#(define-scheme-function (parser location pt)(number?)
   (lambda (grob)
     (let* ((layout (ly:grob-layout grob))
            (ref-size (ly:output-def-lookup (ly:grob-layout grob) 'text-font-size 12)))
       (magnification->font-size (/ pt ref-size))
       )))

\paper{
  <<<!'\n'.join(papier)>>>


  #(define fonts
    (make-pango-font-tree "<<<!proprietes['police_a_roman']>>>"
                          "<<<!proprietes['police_b_sans']>>>"
                          "<<<!proprietes['police_c_mono']>>>"
                           (/ staff-height pt 20)))
  #(set-paper-size "<<<!proprietes['ba_papier']>>>")
  top-margin = <<<!proprietes['marge'][0][:-2] + '\\' + proprietes['marge'][0][-2:]>>>
  bottom-margin = <<<!proprietes['marge'][1][:-2] + '\\' + proprietes['marge'][0][-2:]>>>
  left-margin = <<<!proprietes['marge'][2][:-2] + '\\' + proprietes['marge'][0][-2:]>>>
  right-margin = <<<!proprietes['marge'][3][:-2] + '\\' + proprietes['marge'][0][-2:]>>>
}

\layout {
  \context {
    \Score
    \allowGrobCallback font-interface.font-size
  }
  \context {
    \Global
    \grobdescriptions #all-grob-descriptions
  }
  \context {
    \Lyrics
    \override LyricText . font-name = #"<<<!proprietes['police_a_roman']>>>"
    \override LyricText . font-size = \absFontSize #<<<!proprietes['police_taille']>>>
  }
}

%#(ly:set-option 'safe '#t)

\header{
  tagline = ""
  <<<!'\n'.join(entetes)>>>
  title = "<<<!proprietes['aa_titre']>>>"
}


<<<!contenu>>>
