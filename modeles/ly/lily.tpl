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

#(set-global-staff-size <<<!proprietes['portee_taille']>>>)

#(ly:set-option 'safe '#t)

\header{
  tagline = ""
  <<<!'\n'.join(entetes)>>>
  title = "<<<!proprietes['aa_titre']>>>"
}


<<<!contenu>>>
